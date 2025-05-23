import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import settings to configure environment variables first
from src.services import settings

from src.utils.constants import CENGAGE_GUIDELINES
from src.utils.helpers import get_difficulty_description
from src.utils.utils_mcq import generate_mcqs
from src.utils.utils_fib import generate_fill_in_blank
from src.utils.utils_tf import generate_true_false

# NEW: Import optimized summary helper
from src.utils.summary_helper import generate_content_summary_sync

# print(cengage_guidelines)
# print("-------")
# print(get_difficulty_description("basic"))

# Example of using the optimized version
if __name__ == "__main__":
    print("Testing optimized question generation...")
    
    # First generate shared summary
    print("Generating shared summary...")
    summary = generate_content_summary_sync(
        tenant_id='1305101920',
        filter_key='toc_level_1_title',
        filter_value='01_01920_ch01_ptg01_hires_001-026'
    )
    print(f"Summary generated: {len(summary)} characters")
    
    # Now generate different question types using the shared summary
    print("\\nGenerating MCQs with shared summary...")
    generate_mcqs(
        tenant_id='1305101920',
        filter_key='toc_level_1_title',
        filter_value='01_01920_ch01_ptg01_hires_001-026',
        num_questions=3,
        content_summary=summary  # Use shared summary
    )
    
    print("\\nGenerating True/False with shared summary...")
    generate_true_false(
        tenant_id='1305101920',
        filter_key='toc_level_1_title',
        filter_value='01_01920_ch01_ptg01_hires_001-026',
        num_questions=3,
        content_summary=summary  # Use shared summary
    )
    
    print("\\nGenerating Fill-in-blank with shared summary...")
    generate_fill_in_blank(
        tenant_id='1305101920',
        filter_key='toc_level_1_title',
        filter_value='01_01920_ch01_ptg01_hires_001-026',
        num_questions=3,
        content_summary=summary  # Use shared summary
    )
    
    print("\\n✅ All question types generated using shared summary!")
