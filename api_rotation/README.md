# API Key Rotation System

This directory contains the API key rotation system that automatically cycles through multiple Gemini API keys for each request, ensuring better load distribution and rate limit avoidance.

## 🚀 Features

- **Automatic Rotation**: Each request uses a different API key
- **Thread-Safe**: Works correctly with concurrent requests
- **Persistent**: Rotation state survives application restarts
- **Efficient**: O(1) key retrieval with minimal overhead
- **Fault-Tolerant**: Graceful handling of missing/invalid keys
- **Configurable**: Easy to add/remove API keys

## 📁 Files

- `API_Keys.txt` - Contains the Gemini API keys (one per line)
- `api_key_rotator.py` - Core rotation logic
- `current_index.txt` - Stores current rotation position (auto-generated)
- `test_rotation.py` - Test script for the rotation system
- `demo_rotation.py` - Demonstration of rotation in action
- `README.md` - This documentation file

## 🔧 Setup

1. **Add your API keys** to `API_Keys.txt`:
   ```
   AIzaSyAnPTX7MsR11V0tw2ytvsocUgtmUKn-9FI
   AIzaSyAEZbJCCsepF_9PBn6hUkHXlnrq_Lwz-DA
   AIzaSyDMmNd5xJr7Q9s06FzDkblkKvgqykEJ8qc
   ...
   ```

2. **The system is automatically enabled** when the backend starts
   - No additional configuration required
   - Falls back to settings API key if rotation fails

## 🎯 How It Works

1. **Request comes in** → Chat service calls `get_rotated_model()`
2. **Get next key** → Rotator returns the next API key in sequence
3. **Create model** → New Gemini model created with that specific key
4. **Process request** → Request uses the rotated model
5. **Advance index** → Rotation index moves to next key for next request
6. **Wrap around** → After last key, cycles back to first key

## 🧪 Testing

Run the test script to verify rotation is working:

```bash
python api_rotation/test_rotation.py
```

Run the demo to see rotation in action:

```bash
python api_rotation/demo_rotation.py
```

## 📊 Monitoring

Check rotation status via API endpoint:

```bash
GET /api/chat/api-rotation-status
```

Response:
```json
{
  "enabled": true,
  "stats": {
    "total_keys": 14,
    "current_index": 5,
    "keys_file": "api_rotation/API_Keys.txt",
    "index_file": "api_rotation/current_index.txt",
    "has_keys": true
  },
  "message": "API rotation active with 14 keys"
}
```

## 🔒 Security

- API keys are masked in logs (only first 8 characters shown)
- Keys are stored in plain text file (ensure proper file permissions)
- Consider using environment variables for production deployments

## 🛠️ Troubleshooting

### No API keys found
- Check that `API_Keys.txt` exists and contains valid keys
- Ensure file is in the correct location relative to the application
- Verify file permissions allow reading

### Rotation not working
- Check logs for error messages
- Run test script to verify functionality
- Ensure `current_index.txt` is writable

### Performance issues
- Monitor API key usage across different keys
- Consider adding more keys if hitting rate limits
- Check for any invalid/expired keys

## 🔄 Benefits

- **Load Distribution**: Spreads requests across multiple API keys
- **Rate Limit Avoidance**: Reduces chance of hitting per-key limits
- **High Availability**: No single point of failure
- **Scalability**: Supports more concurrent requests
- **Transparency**: Works seamlessly with existing code

## 📝 Implementation Details

The rotation system is integrated into the chat service at the model creation level:

```python
# Before (single key)
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)

# After (rotated keys)
def get_rotated_model():
    api_key = api_key_rotator.get_next_key()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(settings.GEMINI_MODEL)
```

Each request gets a fresh model instance with a different API key, ensuring proper rotation.

## 🚀 Future Enhancements

- Health checking for individual API keys
- Usage statistics and analytics
- Dynamic key management (add/remove without restart)
- Load balancing based on key performance
- Integration with key management services
