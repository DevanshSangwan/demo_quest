# Gemini API 400 Bad Request Troubleshooting Guide

## Error Description
```
400 Client Error: Bad Request for url: https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent
```

## Potential Causes and Solutions

### 1. **API Version Mismatch** ⚠️ MOST COMMON
**Problem:** Using `/v1/` endpoint when `/v1beta/` is required, or vice versa.

**Solution:** The code has been updated to use `/v1beta/` which is more stable. If you still get errors, try:
- `/v1beta/models/gemini-2.5-flash:generateContent` (current)
- `/v1/models/gemini-2.5-flash:generateContent` (alternative)

### 2. **API Key Authentication Method** 🔑
**Problem:** API key passed incorrectly (header vs query parameter).

**Current Implementation:** Using query parameter `?key={api_key}` (most reliable)

**Alternative if needed:** Use header instead:
```python
headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": api_key
}
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
```

### 3. **Model Name Not Available** 🤖
**Problem:** `gemini-2.5-flash` might not be available in your region or API tier.

**Solutions:**
- Try `gemini-1.5-flash` (more widely available)
- Try `gemini-1.5-pro` (if you have access)
- Check your Google Cloud Console for available models

**To change model:**
```python
# In evaluation.py, line 85, change:
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
```

### 4. **Request Payload Structure** 📦
**Problem:** Missing required fields or incorrect structure.

**Current payload structure:**
```python
{
    "contents": [
        {
            "parts": [
                {
                    "text": "your prompt here"
                }
            ]
        }
    ]
}
```

**Potential issues:**
- Missing `contents` array
- Missing `parts` array
- Text field is empty or None
- Payload is too large (exceeds token limits)

### 5. **Content-Type Header** 📋
**Problem:** Missing or incorrect Content-Type header.

**Solution:** Ensure header is set:
```python
headers = {
    "Content-Type": "application/json",
}
```

### 6. **API Key Permissions** 🔐
**Problem:** API key doesn't have permission for the model or endpoint.

**Check:**
- API key is enabled in Google Cloud Console
- API key has "Generative Language API" enabled
- API key restrictions don't block the request
- Billing is enabled (required for Gemini API)

### 7. **Request Size Limits** 📏
**Problem:** Request payload exceeds size limits.

**Limits:**
- Input tokens: Check model-specific limits
- Output tokens: Check model-specific limits
- Total request size: Usually 32KB for REST API

**Solution:** Reduce prompt size or split into multiple requests.

### 8. **Rate Limiting** ⏱️
**Problem:** Too many requests in short time.

**Solution:** Implement exponential backoff retry logic.

### 9. **Regional Restrictions** 🌍
**Problem:** Model not available in your region.

**Solution:** 
- Check Google Cloud Console for regional availability
- Use a different model that's available in your region
- Use a VPN if necessary (check Google's ToS)

### 10. **API Key Format** 🔑
**Problem:** API key has extra whitespace or is malformed.

**Solution:**
```python
api_key = os.getenv("GEMINI_API_KEY", "").strip()
if not api_key:
    raise HTTPException(...)
```

## Debugging Steps

### Step 1: Check Error Response Details
The updated code now includes detailed error messages. Check the response body for:
- `error.message` - Specific error from Gemini
- `error.code` - Error code
- `error.status` - HTTP status description

### Step 2: Test API Key Directly
Test your API key with curl:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "contents": [{
      "parts": [{
        "text": "Hello"
      }]
    }]
  }'
```

### Step 3: Verify Model Availability
Check available models:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
```

### Step 4: Check Request Payload
Add logging to see the exact payload being sent:
```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Gemini request URL: {url}")
logger.debug(f"Gemini request payload: {json.dumps(request_payload, indent=2)}")
```

### Step 5: Compare with Working PowerShell Command
Since your PowerShell command works, compare:
- Exact URL format
- Header format
- Payload structure
- Model name

## Quick Fixes Applied

1. ✅ Changed from `/v1/` to `/v1beta/` endpoint
2. ✅ Changed API key from header to query parameter
3. ✅ Added detailed error message extraction
4. ✅ Improved error handling to show Gemini's actual error message

## Next Steps if Still Failing

1. **Try different model:**
   - Change `gemini-2.5-flash` to `gemini-1.5-flash` in the URL

2. **Try header authentication:**
   - Change back to using `x-goog-api-key` header instead of query param

3. **Check Google Cloud Console:**
   - Verify API is enabled
   - Check API key restrictions
   - Verify billing is enabled

4. **Test with simpler payload:**
   - Use minimal test payload to isolate the issue

5. **Check logs:**
   - The improved error handling will show Gemini's actual error message
   - This will help identify the specific issue

## Common Error Messages and Solutions

| Error Message | Likely Cause | Solution |
|--------------|--------------|----------|
| "API key not valid" | Invalid or expired key | Regenerate API key in Google Cloud Console |
| "Model not found" | Model name incorrect | Use `gemini-1.5-flash` instead |
| "Quota exceeded" | Rate limit hit | Implement retry with backoff |
| "Billing not enabled" | Billing disabled | Enable billing in Google Cloud Console |
| "Invalid request" | Payload structure wrong | Check payload format matches docs |

