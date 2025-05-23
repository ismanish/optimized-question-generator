"""
Shared summary generation helper for question generators.
This module centralizes the summary generation logic to avoid duplication.
"""
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


async def generate_content_summary(tenant_id: str, filter_key: str, filter_value: str) -> str:
    """
    Generate content summary for the specified filter criteria.
    This is a shared function to avoid generating the same summary multiple times.
    
    Args:
        tenant_id: The tenant ID for the GraphRAG query engine
        filter_key: Metadata field to filter on (e.g., 'toc_level_1_title')
        filter_value: Value to filter by (e.g., chapter ID like '56330_ch10_ptg01')
        
    Returns:
        str: Content summary
    """
    print(f"Generating shared content summary for {filter_key}={filter_value}")
    
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
    
    # Generate comprehensive summary
    summary_query = f"Provide a comprehensive summary of content where {filter_key}={filter_value}. Include key concepts, topics, and important details."
    
    print("Retrieving content summary...")
    summary_response = query_engine.query(summary_query)
    content_summary = summary_response.response
    
    print(f"Summary generated - length: {len(content_summary)} characters")
    return content_summary


def generate_content_summary_sync(tenant_id: str, filter_key: str, filter_value: str) -> str:
    """
    Synchronous version of content summary generation.
    Used when async is not available.
    
    Args:
        tenant_id: The tenant ID for the GraphRAG query engine
        filter_key: Metadata field to filter on
        filter_value: Value to filter by
        
    Returns:
        str: Content summary
    """
    print(f"Generating shared content summary (sync) for {filter_key}={filter_value}")
    
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
    
    # Generate comprehensive summary
    summary_query = f"Provide a comprehensive summary of content where {filter_key}={filter_value}. Include key concepts, topics, and important details."
    
    print("Retrieving content summary...")
    summary_response = query_engine.query(summary_query)
    content_summary = summary_response.response
    
    print(f"Summary generated - length: {len(content_summary)} characters")
    return content_summary
