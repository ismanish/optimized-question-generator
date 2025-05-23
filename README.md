# Optimized Question Generator

This repository contains an optimized version of the question generation API with the following improvements:

1. **Shared Summary Generation**: Summary is generated only once and shared across all question types
2. **Async Processing**: Question generators run in parallel using async/await
3. **Improved Performance**: Significantly reduced processing time

## Key Optimizations

- Created `src/utils/summary_helper.py` for shared summary generation
- Modified question generators to accept pre-generated summaries
- Updated `app.py` to use async processing and generate summary once
- Maintained all existing functionality and input/output formats

## Usage

The API maintains the same interface as the original version. No changes needed for existing clients.
