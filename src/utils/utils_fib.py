import json
import math
import os
import sys
# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import settings first to set environment variables
from src import settings
from src.settings import NeptuneEndpoint, VectorStoreEndpoint

from graphrag_toolkit.lexical_graph.storage import (
    GraphStoreFactory,
    VectorStoreFactory
)
from graphrag_toolkit.lexical_graph import LexicalGraphQueryEngine
from graphrag_toolkit.lexical_graph.metadata import FilterConfig
from llama_index.core.vector_stores.types import (
    MetadataFilter,
    FilterOperator
)
from src.utils.constants import CENGAGE_GUIDELINES as cengage_guidelines
from src.utils.helpers import get_difficulty_description, get_blooms_question_guidelines

def create_question_sequence(question_breakdown):
    """Create a sequence of (difficulty, blooms_level) tuples based on question breakdown"""
    sequence = []
    for combo_key, specs in question_breakdown.items():
        difficulty = specs['difficulty']
        blooms_level = specs['blooms_level']
        count = specs['count']
        
        # Add this combination 'count' times to the sequence
        for _ in range(count):
            sequence.append((difficulty, blooms_level))
    
    return sequence

def parse_fill_in_blank(res, file_name, question_breakdown):
    """Parse Fill-in-blank response and assign metadata programmatically"""
    responses = []
    question_blocks = res.split("QUESTION:")
    
    # Create sequence of difficulty/blooms assignments
    question_sequence = create_question_sequence(question_breakdown)
    question_index = 0
    
    for block in [b.strip() for b in question_blocks if b.strip()]:
        question_obj = {
            "question": "",
            "answer": [],
            "explanation": "",
            "difficulty": "",
            "blooms_level": "",
            "question_type": "fib"
        }
        
        # Extract components using simple string search
        if "ANSWER:" in block:
            question_obj["question"] = block.split("ANSWER:")[0].strip()
            block = "ANSWER:" + block.split("ANSWER:")[1]
        
        if "ANSWER:" in block and "EXPLANATION:" in block:
            answer_text = block.split("ANSWER:")[1].split("EXPLANATION:")[0].strip()
            answer_lines = answer_text.split('\n')
            for line in answer_lines:
                line = line.strip()
                # Check if line starts with a number followed by a period (e.g., "1. ")
                if line and (line[0].isdigit() and '. ' in line):
                    # Remove the numbering and add to the list
                    answer_item = line.split('. ', 1)[1].strip()
                    question_obj["answer"].append(answer_item)
                elif line:  # If there's text but not in numbered format
                    question_obj["answer"].append(line)
        
        if "EXPLANATION:" in block:
            explanation_text = block.split("EXPLANATION:")[1]
            question_obj["explanation"] = explanation_text.strip()
        
        # Programmatically assign difficulty and blooms_level
        if question_index < len(question_sequence):
            difficulty, blooms_level = question_sequence[question_index]
            question_obj["difficulty"] = difficulty
            question_obj["blooms_level"] = blooms_level
            question_index += 1
        
        responses.append(question_obj)

    json_responses = {
        "response": responses
    }
    json_string = json.dumps(json_responses, indent=4)
    with open(file_name, 'w') as json_file:
        json_file.write(json_string)


def generate_fill_in_blank(tenant_id='cx2201', filter_key='toc_level_1_title', filter_value='56330_ch10_ptg01', 
                          num_questions=10, difficulty_distribution={'advanced': 1.0}, 
                          blooms_taxonomy_distribution={'analyze': 1.0}, content_summary=None):
    """
    Generate fill-in-the-blank questions for specified book chapter using GraphRAG with support for difficulty and Bloom's taxonomy distributions
    
    Args:
        tenant_id: The tenant ID for the GraphRAG query engine
        filter_key: Metadata field to filter on (e.g., 'toc_level_1_title')
        filter_value: Value to filter by (e.g., chapter ID like '56330_ch10_ptg01')
        num_questions: Number of fill-in-the-blank questions to generate
        difficulty_distribution: Dict with difficulty distribution e.g., {'basic': 0.3, 'intermediate': 0.3, 'advanced': 0.4}
        blooms_taxonomy_distribution: Dict with Bloom's distribution e.g., {'remember': 0.3, 'apply': 0.4, 'analyze': 0.3}
        content_summary: Pre-generated content summary (NEW: avoids duplicate summary generation)
        
    Returns:
        Dict containing the generated fill-in-the-blank questions
    """
    print(f"Generating {num_questions} fill-in-the-blank questions for {filter_key}={filter_value}")
    print(f"Difficulty distribution: {difficulty_distribution}")
    print(f"Bloom's taxonomy distribution: {blooms_taxonomy_distribution}")
    
    # Use provided summary or generate one (fallback for backward compatibility)
    if content_summary is None:
        print("Warning: No content summary provided, generating new one...")
        # Initialize stores using the endpoint constants
        graph_store = GraphStoreFactory.for_graph_store(NeptuneEndpoint)
        vector_store = VectorStoreFactory.for_vector_store(VectorStoreEndpoint)
        
        # Set up metadata filter
        metadata_filter = MetadataFilter(
            key=filter_key,
            value=filter_value,
            operator=FilterOperator.EQ
        )
        
        filter_config = FilterConfig(source_filters=metadata_filter)
        
        # Initialize query engine with filter
        query_engine = LexicalGraphQueryEngine.for_traversal_based_search(
            graph_store,
            vector_store,
            filter_config=filter_config,
            tenant_id=tenant_id,
            llm_config={
                "model": "arn:aws:bedrock:us-east-1:051826717360:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                "temperature": 0,
                "max_tokens": 10000,
                "system_prompt": cengage_guidelines
            }
        )
        
        # Generate content summary
        summary_query = f"Provide a comprehensive summary of content where {filter_key}={filter_value}. Include key concepts, topics, and important details."
        print("Retrieving content summary...")
        summary_response = query_engine.query(summary_query)
        content_summary = summary_response.response
        print(f"Summary length: {len(content_summary)} characters")
    else:
        print(f"Using provided content summary (length: {len(content_summary)} characters)")
        
        # Still need query engine for question generation
        graph_store = GraphStoreFactory.for_graph_store(NeptuneEndpoint)
        vector_store = VectorStoreFactory.for_vector_store(VectorStoreEndpoint)
        
        metadata_filter = MetadataFilter(
            key=filter_key,
            value=filter_value,
            operator=FilterOperator.EQ
        )
        
        filter_config = FilterConfig(source_filters=metadata_filter)
        
        query_engine = LexicalGraphQueryEngine.for_traversal_based_search(
            graph_store,
            vector_store,
            filter_config=filter_config,
            tenant_id=tenant_id,
            llm_config={
                "model": "arn:aws:bedrock:us-east-1:051826717360:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                "temperature": 0,
                "max_tokens": 10000,
                "system_prompt": cengage_guidelines
            }
        )

    # Calculate questions for each combination of difficulty and bloom's level
    question_breakdown = {}
    for difficulty, diff_ratio in difficulty_distribution.items():
        for blooms, blooms_ratio in blooms_taxonomy_distribution.items():
            count = int(round(num_questions * diff_ratio * blooms_ratio))
            if count > 0:
                question_breakdown[f"{difficulty}_{blooms}"] = {
                    'difficulty': difficulty,
                    'blooms_level': blooms,
                    'count': count
                }
    
    # Adjust to ensure total matches exactly
    total_calculated = sum([item['count'] for item in question_breakdown.values()])
    if total_calculated != num_questions:
        # Add/subtract from the largest group
        largest_key = max(question_breakdown.keys(), key=lambda k: question_breakdown[k]['count'])
        question_breakdown[largest_key]['count'] += (num_questions - total_calculated)
    
    print(f"Question breakdown: {question_breakdown}")
    
    # Generate all questions in a single prompt with specific guidelines
    all_guidelines = []
    
    for combo_key, specs in question_breakdown.items():
        difficulty = specs['difficulty']
        blooms_level = specs['blooms_level']
        count = specs['count']
        
        guidelines = get_blooms_question_guidelines(blooms_level, "fib")
        difficulty_desc = get_difficulty_description(difficulty)
        
        all_guidelines.append(f"""
For {count} questions at {difficulty.upper()} difficulty and {blooms_level.upper()} Bloom's level:
- Difficulty: {difficulty_desc}
- Bloom's Level Guidelines: {guidelines}
        """)
    
    # Generate filename based on distributions
    difficulty_str = "_".join([f"{diff}{int(prop*100)}" for diff, prop in difficulty_distribution.items()])
    blooms_str = "_".join([f"{bloom}{int(prop*100)}" for bloom, prop in blooms_taxonomy_distribution.items()])
    file_name = f"{filter_value}_{difficulty_str}_{blooms_str}_fib.json"
    
    # Generate fill-in-the-blank questions based on summary
    fib_prompt = f"""
    You are a professor writing sophisticated fill-in-the-blank questions for an upper-level university course. The questions will be based on this chapter summary:

    {content_summary}

    Create exactly {num_questions} fill-in-the-blank questions following these specific guidelines:

    {' '.join(all_guidelines)}

    IMPORTANT FORMATTING INSTRUCTIONS:
    - Start IMMEDIATELY with your first question using "QUESTION:" 
    - DO NOT write ANY introductory text like "Based on the chapter..." or "I'll create..."
    - DO NOT include ANY preamble or explanation before the first question
    - Each blank should be indicated by "________" (8 underscores)
    - A question may have multiple blanks if appropriate

    Each question should:
    1. Match the specified difficulty and Bloom's taxonomy level
    2. Present statements appropriate to the cognitive level required
    3. Use domain-specific terminology accurately
    4. Focus on important concepts from the chapter

    Format each question exactly as follows:
    QUESTION: [Statement with ________ for blanks, appropriate to difficulty and Bloom's level]
    ANSWER: [Correct answer(s) that should fill the blank(s), if multiple blanks, list each answer separately]
    EXPLANATION: [Explanation of why this is the correct answer and how it demonstrates the required cognitive level]

    Distribution of questions:
    {question_breakdown}
    
    Make sure to vary the cognitive demands according to the Bloom's taxonomy levels specified.
    """
    
    print("Generating fill-in-the-blank questions...")
    fib_response = query_engine.query(fib_prompt)
    fib_text = fib_response.response

    # Pass question_breakdown to parsing function
    parse_fill_in_blank(res=fib_text, file_name=file_name, question_breakdown=question_breakdown)
    
    print(f"Generated fill-in-the-blank questions and saved to {file_name}")
    return fib_text


if __name__ == "__main__":
    # Example with distributions: 30% basic, 30% intermediate, 40% advanced
    # and 20% remember, 50% apply, 30% analyze
    difficulty_dist = {
        'basic': 0.3,
        'intermediate': 0.3,
        'advanced': 0.4
    }
    
    blooms_dist = {
        'remember': 0.2,
        'apply': 0.5,
        'analyze': 0.3
    }
    
    print("Testing Fill-in-the-Blank generation with mixed distributions...")
    result = generate_fill_in_blank(
        tenant_id='1305101920',
        filter_key='toc_level_1_title',
        filter_value='01_01920_ch01_ptg01_hires_001-026',
        num_questions=10,
        difficulty_distribution=difficulty_dist,
        blooms_taxonomy_distribution=blooms_dist
    )
    print(f"Fill-in-the-blank generation completed. Check the generated JSON file for results.")
