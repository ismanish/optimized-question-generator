import sys
import os
import uuid
import json
import datetime
import boto3
import math
import asyncio
import concurrent.futures
from typing import Optional, Dict
from fastapi import FastAPI, Query, HTTPException, Depends
from pydantic import BaseModel, Field
from enum import Enum
from fastapi.responses import JSONResponse

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import settings to configure environment variables first
from src import settings

# Import question generation functions - OPTIMIZED VERSION
from src.utils.helpers import get_difficulty_description

# Import the NEW shared summary helper
from src.utils.summary_helper import generate_content_summary_sync

# Initialize DynamoDB client
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.environ.get('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

# Get the DynamoDB table
table_name = 'question_generation_history'
try:
    table = dynamodb.Table(table_name)
    # Test if table exists by performing a small operation
    table.scan(Limit=1)
    print(f"Successfully connected to DynamoDB table: {table_name}")
except Exception as e:
    print(f"Warning: DynamoDB table access error - {str(e)}")
    print("Will log to console instead of DynamoDB")
    table = None

app = FastAPI(
    title="Question Generation API - OPTIMIZED",
    description="Optimized API for generating different types of questions using GraphRAG with async processing and shared summary generation",
    version="2.0.0"
)

class QuestionType(str, Enum):
    mcq = "mcq"
    tf = "tf"
    fib = "fib"

class BloomsTaxonomy(str, Enum):
    remember = "remember"
    apply = "apply"
    analyze = "analyze"

class DifficultyLevel(str, Enum):
    basic = "basic"
    intermediate = "intermediate"
    advanced = "advanced"

class QuestionRequest(BaseModel):
    tenant_id: str = "1305101920"
    filter_key: str = "toc_level_1_title"
    filter_value: str = "01_01920_ch01_ptg01_hires_001-026"
    total_questions: int = 10
    question_type_distribution: Dict[str, float] = {"mcq": 0.4, "fib": 0.3, "tf": 0.3}
    difficulty_distribution: Dict[str, float] = {"basic": 0.3, "intermediate": 0.3, "advanced": 0.4}
    blooms_taxonomy_distribution: Dict[str, float] = {"remember": 0.3, "apply": 0.4, "analyze": 0.3}
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique session identifier")

class QuestionResponse(BaseModel):
    status: str
    message: str
    files_generated: list
    data: dict

def calculate_question_distribution(total_questions: int, question_type_dist: Dict[str, float], 
                                  difficulty_dist: Dict[str, float], blooms_dist: Dict[str, float]):
    """
    Calculate the exact number of questions for each combination of question type, difficulty, and bloom's level
    """
    distribution = {}
    
    for q_type, q_ratio in question_type_dist.items():
        q_count = int(round(total_questions * q_ratio))
        
        for difficulty, d_ratio in difficulty_dist.items():
            d_count = int(round(q_count * d_ratio))
            
            for blooms, b_ratio in blooms_dist.items():
                b_count = int(round(d_count * b_ratio))
                
                if b_count > 0:
                    key = f"{q_type}_{difficulty}_{blooms}"
                    distribution[key] = {
                        'question_type': q_type,
                        'difficulty': difficulty,
                        'blooms_level': blooms,
                        'count': b_count
                    }
    
    # Adjust counts to ensure total matches exactly
    total_calculated = sum([item['count'] for item in distribution.values()])
    if total_calculated != total_questions:
        # Add/subtract from the largest group
        largest_key = max(distribution.keys(), key=lambda k: distribution[k]['count'])
        distribution[largest_key]['count'] += (total_questions - total_calculated)
    
    return distribution

def generate_single_question_type_sync(question_type: str, configs: list, content_summary: str, 
                                      tenant_id: str, filter_key: str, filter_value: str,
                                      difficulty_distribution: Dict[str, float], 
                                      blooms_distribution: Dict[str, float]) -> tuple:
    """
    Synchronous function for generating a single question type using shared summary.
    This function will be run in parallel using ThreadPoolExecutor.
    """
    try:
        # Import functions inside the function to avoid import issues
        from src.utils.utils_mcq import generate_mcqs
        from src.utils.utils_fib import generate_fill_in_blank  
        from src.utils.utils_tf import generate_true_false
        
        # Aggregate counts for this question type
        total_for_type = sum([config['count'] for config in configs])
        
        print(f"[THREAD] Generating {question_type} questions (count: {total_for_type})...")
        
        # Generate questions based on type using the OPTIMIZED functions with shared summary
        if question_type == "mcq":
            question_text = generate_mcqs(
                tenant_id=tenant_id,
                filter_key=filter_key,
                filter_value=filter_value,
                num_questions=total_for_type,
                difficulty_distribution=difficulty_distribution,
                blooms_taxonomy_distribution=blooms_distribution,
                content_summary=content_summary
            )
        elif question_type == "fib":
            question_text = generate_fill_in_blank(
                tenant_id=tenant_id,
                filter_key=filter_key,
                filter_value=filter_value,
                num_questions=total_for_type,
                difficulty_distribution=difficulty_distribution,
                blooms_taxonomy_distribution=blooms_distribution,
                content_summary=content_summary
            )
        elif question_type == "tf":
            question_text = generate_true_false(
                tenant_id=tenant_id,
                filter_key=filter_key,
                filter_value=filter_value,
                num_questions=total_for_type,
                difficulty_distribution=difficulty_distribution,
                blooms_taxonomy_distribution=blooms_distribution,
                content_summary=content_summary
            )
        
        # Generate filename exactly as the utility functions do
        difficulty_str = "_".join([f"{diff}{int(prop*100)}" for diff, prop in difficulty_distribution.items()])
        blooms_str = "_".join([f"{bloom}{int(prop*100)}" for bloom, prop in blooms_distribution.items()])
        
        if question_type == "mcq":
            file_name = f"{filter_value}_{difficulty_str}_{blooms_str}_mcqs.json"
        elif question_type == "fib":
            file_name = f"{filter_value}_{difficulty_str}_{blooms_str}_fib.json"
        elif question_type == "tf":
            file_name = f"{filter_value}_{difficulty_str}_{blooms_str}_tf.json"
        
        # Read the generated JSON file
        with open(file_name, 'r') as json_file:
            question_data = json.load(json_file)
        
        print(f"[THREAD] Completed generating {question_type} questions")
        return question_type, file_name, question_data, None
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[THREAD] Error generating {question_type} questions: {str(e)}")
        print(f"[THREAD] Full error details: {error_details}")
        return question_type, None, None, str(e)

@app.get("/")
def read_root():
    return {"message": "Question Generation API v2.0 - OPTIMIZED. Use /questionBankService/source/{sourceId}/questions/generate endpoint to create questions with TRUE parallel processing and shared summary generation."}

@app.post("/questionBankService/source/{sourceId}/questions/generate", response_model=QuestionResponse)
async def generate_questions(sourceId: str, request: QuestionRequest):
    """
    Generate questions based on the specified parameters with OPTIMIZED async processing and shared summary generation.
    
    Key Optimizations:
    1. Summary generated only ONCE and shared across all question types
    2. Question generators run in TRUE PARALLEL using ThreadPoolExecutor
    3. Significantly improved performance
    
    - **sourceId**: Source identifier (e.g., 'dev_app')
    - **tenant_id**: The tenant ID for the GraphRAG query engine
    - **filter_key**: Metadata field to filter on (e.g., 'toc_level_1_title')
    - **filter_value**: Value to filter by (e.g., chapter ID like '56330_ch10_ptg01')
    - **total_questions**: Total number of questions to generate
    - **question_type_distribution**: Distribution of question types (mcq, fib, tf)
    - **difficulty_distribution**: Distribution of difficulty levels (basic, intermediate, advanced)
    - **blooms_taxonomy_distribution**: Distribution of Bloom's levels (remember, apply, analyze)
    - **session_id**: Unique session identifier for tracking this request
    """
    # Generate timestamp for the request
    request_timestamp = datetime.datetime.utcnow().isoformat()
    status = "success"
    error_message = ""
    all_question_data = {}
    files_generated = []
    
    print(f"Processing OPTIMIZED request for sourceId: {sourceId}")
    print(f"Request parameters: {request.dict()}")
    
    try:
        # OPTIMIZATION 1: Generate shared summary ONCE
        print("🚀 OPTIMIZATION: Generating shared content summary once...")
        start_time = datetime.datetime.utcnow()
        
        # Generate the summary once using the shared helper
        content_summary = generate_content_summary_sync(
            tenant_id=request.tenant_id,
            filter_key=request.filter_key,
            filter_value=request.filter_value
        )
        
        summary_time = (datetime.datetime.utcnow() - start_time).total_seconds()
        print(f"✅ Shared summary generated in {summary_time:.2f} seconds (length: {len(content_summary)} characters)")
        
        # Calculate question distribution
        question_dist = calculate_question_distribution(
            request.total_questions,
            request.question_type_distribution,
            request.difficulty_distribution,
            request.blooms_taxonomy_distribution
        )
        
        print(f"Question distribution: {question_dist}")
        
        # Group by question type for generation
        type_groups = {}
        for key, config in question_dist.items():
            q_type = config['question_type']
            if q_type not in type_groups:
                type_groups[q_type] = []
            type_groups[q_type].append(config)
        
        # OPTIMIZATION 2: Run question generators in TRUE PARALLEL using ThreadPoolExecutor
        print("🚀 OPTIMIZATION: Running question generators in TRUE PARALLEL using threads...")
        parallel_start_time = datetime.datetime.utcnow()
        
        # Create thread pool and submit tasks
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Create futures for each question type
            futures = []
            
            for question_type, configs in type_groups.items():
                # Create combined distributions for this question type
                total_for_type = sum([config['count'] for config in configs])
                difficulty_dist_for_type = {}
                blooms_dist_for_type = {}
                
                for config in configs:
                    diff = config['difficulty']
                    blooms = config['blooms_level']
                    count = config['count']
                    
                    if diff not in difficulty_dist_for_type:
                        difficulty_dist_for_type[diff] = 0
                    if blooms not in blooms_dist_for_type:
                        blooms_dist_for_type[blooms] = 0
                        
                    difficulty_dist_for_type[diff] += count / total_for_type
                    blooms_dist_for_type[blooms] += count / total_for_type
                
                # Submit task to thread pool
                future = loop.run_in_executor(
                    executor,
                    generate_single_question_type_sync,
                    question_type,
                    configs,
                    content_summary,  # Pass shared summary
                    request.tenant_id,
                    request.filter_key,
                    request.filter_value,
                    difficulty_dist_for_type,
                    blooms_dist_for_type
                )
                futures.append(future)
            
            # Wait for all futures to complete - THIS IS TRUE PARALLEL EXECUTION
            print(f"⚡ Running {len(futures)} question generators in parallel threads...")
            results = await asyncio.gather(*futures, return_exceptions=True)
        
        parallel_time = (datetime.datetime.utcnow() - parallel_start_time).total_seconds()
        print(f"✅ TRUE parallel question generation completed in {parallel_time:.2f} seconds")
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                raise result
            
            question_type, file_name, question_data, error = result
            
            if error:
                raise Exception(f"Error in {question_type}: {error}")
            
            files_generated.append(file_name)
            all_question_data[question_type] = question_data
        
        total_time = (datetime.datetime.utcnow() - start_time).total_seconds()
        
        response = QuestionResponse(
            status=status,
            message=f"✅ OPTIMIZED: Generated {request.total_questions} questions across {len(type_groups)} question types for sourceId: {sourceId} in {total_time:.2f} seconds (Summary: {summary_time:.2f}s, TRUE Parallel Generation: {parallel_time:.2f}s)",
            files_generated=files_generated,
            data=all_question_data
        )
        
    except Exception as e:
        import traceback
        error_message = str(e)
        error_details = traceback.format_exc()
        print(f"Full error details: {error_details}")
        status = "error"
        response = QuestionResponse(
            status=status,
            message=f"❌ Error generating questions for sourceId {sourceId}: {error_message}",
            files_generated=[],
            data={}
        )
        raise HTTPException(status_code=500, detail=f"Error generating questions: {error_message}")
    finally:
        # Store the request and response data in DynamoDB
        try:
            if table is not None:
                # Create item to store in DynamoDB
                dynamo_item = {
                    'session_id': request.session_id,
                    'source_id': sourceId,
                    'request_timestamp': request_timestamp,
                    'tenant_id': request.tenant_id,
                    'filter_key': request.filter_key,
                    'filter_value': request.filter_value,
                    'total_questions': request.total_questions,
                    'question_type_distribution': json.dumps(request.question_type_distribution),
                    'difficulty_distribution': json.dumps(request.difficulty_distribution),
                    'blooms_taxonomy_distribution': json.dumps(request.blooms_taxonomy_distribution),
                    'files_generated': json.dumps(files_generated),
                    'status': status,
                    'error_message': error_message,
                    'response_data': json.dumps(all_question_data) if all_question_data else ""
                }
                
                # Put item in DynamoDB
                table.put_item(Item=dynamo_item)
                print(f"Request data saved to DynamoDB for session: {request.session_id}, sourceId: {sourceId}")
            else:
                # Log to console if DynamoDB is not available
                print(f"Request data (not saved to DynamoDB): sourceId={sourceId}, {request.dict()}")
        except Exception as db_error:
            print(f"Error saving to DynamoDB: {str(db_error)}")
    
    # If we got here without raising an exception, return the response
    if status == "success":
        return response

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0 - OPTIMIZED", "optimizations": ["shared_summary_generation", "true_parallel_processing_with_threads"]}

# Run the FastAPI app with uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
