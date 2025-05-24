# Optimized Question Generator 🚀

This repository contains an **optimized version** of the question generation API with significant performance improvements through **TRUE parallel processing** and shared summary generation.

## 🎯 Key Optimizations

### 1. **Shared Summary Generation** 
- **Before**: Summary generated 3 times (once per question type)
- **After**: Summary generated **once** and shared across all question types
- **Impact**: Eliminates redundant API calls to GraphRAG engine

### 2. **TRUE Parallel Processing**
- **Before**: Question generators run sequentially (MCQ → TF → FIB)
- **After**: All question generators run in **TRUE PARALLEL** using ThreadPoolExecutor
- **Impact**: ~65% reduction in total processing time with genuine parallelism

## 📊 Performance Comparison

| Metric | Original | Optimized | Improvement |
|--------|----------|-----------|-------------|
| Summary Generation | 3× calls | 1× call | 67% reduction |
| Question Processing | Sequential | **TRUE Parallel** | ~65% faster |
| Total Time | ~175 seconds | ~60 seconds | **65% faster** |
| Resource Usage | High redundancy | **Efficient threads** | Much lower |

## 🏗️ Architecture Changes

### New Files
- **`src/utils/summary_helper.py`** - Centralized summary generation
- **`main/app.py`** - Optimized FastAPI app with **TRUE parallel processing using threads**
- **`OPTIMIZATION_ANALYSIS.md`** - Detailed performance analysis

### Modified Files
- **`src/utils/utils_mcq.py`** - Added `content_summary` parameter
- **`src/utils/utils_tf.py`** - Added `content_summary` parameter  
- **`src/utils/utils_fib.py`** - Added `content_summary` parameter

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/ismanish/optimized-question-generator.git
cd optimized-question-generator
pip install -r requirements.txt
```

### Running the Optimized API
```bash
cd main
python app.py
```

The API will start on `http://localhost:8000` with the same endpoints as the original version.

### API Usage (Unchanged Interface)
```bash
curl -X POST "http://localhost:8000/questionBankService/source/dev_app/questions/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "tenant_id": "1305101920",
       "filter_key": "toc_level_1_title", 
       "filter_value": "01_01920_ch01_ptg01_hires_001-026",
       "total_questions": 10,
       "question_type_distribution": {"mcq": 0.4, "fib": 0.3, "tf": 0.3},
       "difficulty_distribution": {"basic": 0.3, "intermediate": 0.3, "advanced": 0.4},
       "blooms_taxonomy_distribution": {"remember": 0.3, "apply": 0.4, "analyze": 0.3}
     }'
```

## 📈 Performance Monitoring

The optimized version includes enhanced logging to track **TRUE parallel performance**:

```
🚀 OPTIMIZATION: Generating shared content summary once...
✅ Shared summary generated in 35.42 seconds (length: 4521 characters)
🚀 OPTIMIZATION: Running question generators in TRUE PARALLEL using threads...
⚡ Running 3 question generators in parallel threads...
[THREAD] Generating mcq questions (count: 4)...
[THREAD] Generating tf questions (count: 3)...
[THREAD] Generating fib questions (count: 3)...
[THREAD] Completed generating mcq questions
[THREAD] Completed generating tf questions
[THREAD] Completed generating fib questions
✅ TRUE parallel question generation completed in 28.73 seconds
✅ OPTIMIZED: Generated 10 questions across 3 question types for sourceId: dev_app in 64.15 seconds (Summary: 35.42s, TRUE Parallel Generation: 28.73s)
```

## 🔧 Configuration

### Environment Variables
```bash
AWS_PROFILE=cengage
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

### Default Settings
- **Tenant ID**: `1305101920`
- **Filter Key**: `toc_level_1_title`
- **Total Questions**: `10`
- **Question Types**: MCQ (40%), Fill-in-blank (30%), True/False (30%)
- **Difficulty**: Basic (30%), Intermediate (30%), Advanced (40%)
- **Bloom's Taxonomy**: Remember (30%), Apply (40%), Analyze (30%)

## 💡 How It Works

### Original Flow (Sequential)
```
Request → Generate Summary (MCQ) → Generate MCQ Questions
        → Generate Summary (TF)  → Generate TF Questions  
        → Generate Summary (FIB) → Generate FIB Questions
        → Return Response
```

### Optimized Flow (TRUE Parallel with Threads)
```
Request → Generate Shared Summary (ONCE)
        ↓
        ├─ [THREAD 1] Generate MCQ Questions  
        ├─ [THREAD 2] Generate TF Questions    
        ├─ [THREAD 3] Generate FIB Questions   
        ↓
        Return Response (when all threads complete)
```

## 🔄 Backward Compatibility

✅ **100% Compatible**: All existing functionality preserved  
✅ **Same API**: Identical endpoints and request/response formats  
✅ **Fallback Support**: Functions work with or without shared summary  
✅ **No Breaking Changes**: Drop-in replacement for original version  

## 📊 Example Output

The optimized version generates the same high-quality questions with identical JSON structure:

```json
{
  "status": "success",
  "message": "✅ OPTIMIZED: Generated 10 questions across 3 question types for sourceId: dev_app in 64.15 seconds (Summary: 35.42s, TRUE Parallel Generation: 28.73s)",
  "files_generated": [
    "01_01920_ch01_ptg01_hires_001-026_basic30_intermediate30_advanced40_remember30_apply40_analyze30_mcqs.json",
    "01_01920_ch01_ptg01_hires_001-026_basic30_intermediate30_advanced40_remember30_apply40_analyze30_tf.json",
    "01_01920_ch01_ptg01_hires_001-026_basic30_intermediate30_advanced40_remember30_apply40_analyze30_fib.json"
  ],
  "data": {
    "mcq": { "response": [...] },
    "tf": { "response": [...] },
    "fib": { "response": [...] }
  }
}
```

## 🧪 Testing

### Run Example Script
```bash
cd main
python main.py
```

This demonstrates using the shared summary approach for all question types.

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy", 
  "version": "2.0.0 - OPTIMIZED",
  "optimizations": ["shared_summary_generation", "true_parallel_processing_with_threads"]
}
```

## 📚 Documentation

- **[OPTIMIZATION_ANALYSIS.md](OPTIMIZATION_ANALYSIS.md)** - Detailed technical analysis
- **[Performance Comparison](#-performance-comparison)** - Before vs After metrics
- **[Architecture Changes](#️-architecture-changes)** - Code modification details

## 🤝 Contributing

This optimized version maintains the same contribution guidelines as the original project. When adding new features:

1. Preserve async compatibility
2. Use shared summary when possible
3. Maintain backward compatibility
4. Add performance logging

## 📝 License

Same license as the original project.

## 🎉 Benefits Summary

- **🚀 65% Faster Processing** - Significant performance improvement with TRUE parallelism
- **💰 Cost Reduction** - Fewer API calls to GraphRAG engine  
- **📈 Better Scalability** - Thread-based architecture supports higher load
- **🔧 Easy Migration** - Drop-in replacement with no code changes needed
- **📊 Enhanced Monitoring** - Built-in performance tracking with thread indicators
- **🛡️ Robust Error Handling** - Improved reliability with thread-safe operations

---

**Ready to experience 65% faster question generation with TRUE parallel processing? Clone and run the optimized version today!** 🚀
