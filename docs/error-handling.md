# Error Handling Strategy

## External API
- Wrapped in try/except  
- 5‑second timeout  
- Clear JSON error messages  
- Retry logic for `EXTERNAL_API_URL`  
- Cached fallback if retries fail

## Supabase
- Checks for missing environment variables  
- Handles non‑200 responses  
- Returns structured error messages  

## Flask
- Ensures all endpoints return valid JSON  
- Prevents crashes from API failures  

