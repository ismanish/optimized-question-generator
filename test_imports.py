#!/usr/bin/env python3
"""
Simple test script to verify the function signatures and imports
"""
import sys
import os
import inspect

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Testing imports and function signatures...")
print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")

try:
    # Test importing settings
    print("\n1. Testing settings import...")
    from src import settings
    print("✅ Settings imported successfully")
    
    # Test importing utils
    print("\n2. Testing utils imports...")
    from src.utils.utils_mcq import generate_mcqs
    from src.utils.utils_fib import generate_fill_in_blank
    from src.utils.utils_tf import generate_true_false
    print("✅ All utils imported successfully")
    
    # Test function signatures
    print("\n3. Testing function signatures...")
    
    # Check MCQ function signature
    mcq_sig = inspect.signature(generate_mcqs)
    print(f"MCQ signature: {mcq_sig}")
    print(f"MCQ parameters: {list(mcq_sig.parameters.keys())}")
    
    # Check if content_summary parameter exists
    if 'content_summary' in mcq_sig.parameters:
        print("✅ content_summary parameter found in generate_mcqs")
    else:
        print("❌ content_summary parameter NOT found in generate_mcqs")
    
    # Check TF function signature
    tf_sig = inspect.signature(generate_true_false)
    print(f"TF signature: {tf_sig}")
    if 'content_summary' in tf_sig.parameters:
        print("✅ content_summary parameter found in generate_true_false")
    else:
        print("❌ content_summary parameter NOT found in generate_true_false")
    
    # Check FIB function signature
    fib_sig = inspect.signature(generate_fill_in_blank)
    print(f"FIB signature: {fib_sig}")
    if 'content_summary' in fib_sig.parameters:
        print("✅ content_summary parameter found in generate_fill_in_blank")
    else:
        print("❌ content_summary parameter NOT found in generate_fill_in_blank")
    
    print("\n4. Testing function calls with content_summary...")
    
    # Test calling the function with content_summary parameter
    try:
        # This should work if the parameter exists
        print("Testing MCQ with content_summary...")
        result = generate_mcqs(
            tenant_id='test',
            filter_key='test',
            filter_value='test',
            num_questions=1,
            content_summary="test summary"
        )
        print("✅ MCQ function accepts content_summary parameter")
    except TypeError as e:
        print(f"❌ MCQ function call failed: {e}")
    
except Exception as e:
    print(f"❌ Import/test failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTest completed!")
