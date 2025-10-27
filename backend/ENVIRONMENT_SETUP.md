# Environment Setup and NLTK Configuration

This document explains how to set up the environment for the Learning App backend, including NLTK data initialization for LlamaIndex integration.

## NLTK Data Setup

The application uses NLTK (Natural Language Toolkit) for text processing, particularly through LlamaIndex for large document handling. NLTK data must be properly initialized to avoid errors like `zipfile.BadZipFile`.

### Automatic Initialization

NLTK data is automatically initialized when the FastAPI server starts. The initialization:

1. **Downloads required NLTK resources**:
   - `punkt`: Sentence tokenizer (required by LlamaIndex)
   - `stopwords`: Stop words for text processing
   - `wordnet`: WordNet for semantic analysis
   - `averaged_perceptron_tagger`: POS tagger

2. **Handles corrupted data**: Automatically detects and removes corrupted NLTK data files, then re-downloads fresh copies.

3. **Provides graceful error handling**: If NLTK operations fail, the system attempts to auto-download missing resources and retry operations.

### Manual Setup (if needed)

If you encounter NLTK-related errors, you can manually initialize the data:

```python
import nltk
from utils.nltk_init import initialize_nltk_data

# Initialize NLTK data
initialize_nltk_data()

# Or download specific resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
```

### Environment Variables

Set the following environment variable to customize NLTK data location:

```bash
export NLTK_DATA=/path/to/nltk_data
```

If not set, NLTK data will be stored in `~/nltk_data` by default.

### Troubleshooting

#### Common Errors

1. **zipfile.BadZipFile: File is not a zip file**
   - **Cause**: NLTK data files are corrupted or incomplete
   - **Solution**: The system automatically detects and removes corrupted files, then re-downloads them

2. **LookupError: NLTK data not found**
   - **Cause**: Required NLTK resources are missing
   - **Solution**: The system automatically downloads missing resources on first use

3. **Network timeout during download**
   - **Cause**: Slow internet connection or firewall blocking NLTK downloads
   - **Solution**: Ensure internet connectivity and try again, or manually download resources

#### Verifying Installation

Check if NLTK data is properly installed:

```python
import nltk
try:
    nltk.data.find('tokenizers/punkt')
    print("NLTK punkt tokenizer is available")
except LookupError:
    print("NLTK punkt tokenizer is missing")
```

### Integration with LlamaIndex

NLTK is used by LlamaIndex for:

- **Sentence splitting**: Breaking documents into sentences for better chunking
- **Text tokenization**: Preparing text for embedding generation
- **Stop word removal**: Improving retrieval quality

The LlamaIndex service includes fallback mechanisms:
- If NLTK operations fail, it falls back to simpler tokenization methods
- If sentence splitting fails, it uses basic text chunking
- All errors are logged with helpful messages for debugging

### Development vs Production

#### Development
- NLTK data is downloaded automatically on first run
- Data is stored in user's home directory (`~/nltk_data`)
- No additional setup required

#### Production
- Consider pre-downloading NLTK data during Docker build
- Set `NLTK_DATA` environment variable to a persistent volume
- Monitor logs for NLTK-related errors and ensure network access for auto-downloads

### Logs

NLTK initialization logs can be found in the application logs:

```
INFO - Initializing NLTK data...
INFO - NLTK data directory: /home/user/nltk_data
INFO - Downloading NLTK resource: punkt
INFO - Successfully downloaded NLTK resource: punkt
INFO - NLTK data initialization completed
```

If errors occur:

```
WARNING - NLTK resource punkt is missing
ERROR - Failed to download NLTK resource punkt: [error details]
```

## LlamaIndex Configuration

See `backend/config/settings.py` for LlamaIndex-specific settings:

- `LLAMAINDEX_CHUNK_SIZE`: Chunk size for document splitting (default: 1000)
- `LLAMAINDEX_CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `LLAMAINDEX_USE_FOR_LARGE_PDFS`: Enable LlamaIndex for large PDFs (default: true)
- `LLAMAINDEX_LARGE_PDF_THRESHOLD_MB`: Size threshold for large PDF detection (default: 10)

## Testing

Run the following to test NLTK integration:

```python
# Test basic NLTK functionality
from utils.nltk_init import safe_nltk_operation
import nltk

result = safe_nltk_operation("sent_tokenize", nltk.sent_tokenize, "This is a test sentence. This is another sentence.")
print(f"Sentence tokenization result: {result}")

# Test LlamaIndex integration
from services.llamaindex_service import llamaindex_service
print("LlamaIndex service initialized successfully")