# Troubleshooting Login 500 Error

## Issue
Getting 500 Internal Server Error on `/api/auth/login` endpoint in production (Vercel).

## Root Causes & Solutions

### 1. **Cold Start Issue** ✅ FIXED
**Problem**: On Vercel, each serverless function starts fresh. The `users.json` file doesn't exist initially.

**Solution**: 
- Added demo user initialization on startup event
- Added fallback initialization in login endpoint
- Users are created automatically if file doesn't exist

### 2. **File Path Issue** ✅ FIXED
**Problem**: Writing to project root fails on Vercel (read-only filesystem).

**Solution**:
- Changed `users.json` → `/tmp/users.json` on Vercel
- Changed `memory_bank.json` → `/tmp/memory_bank.json` on Vercel
- Changed `uploads/` → `/tmp/uploads/` on Vercel

### 3. **JWT_SECRET_KEY Not Set** ⚠️ CHECK
**Problem**: If `JWT_SECRET_KEY` is not set, tokens might fail.

**Solution**:
- Set `JWT_SECRET_KEY` in Vercel environment variables
- Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

### 4. **Error Handling** ✅ IMPROVED
**Problem**: Errors were not logged, making debugging difficult.

**Solution**:
- Added comprehensive error logging with traceback
- Added error events for observability
- Better error messages returned to client

## Testing Locally

```bash
# Start server
source venv/bin/activate
uvicorn app.api_server:app --host 0.0.0.0 --port 8000

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"patient@demo.com","password":"patient123"}'
```

## Verification Checklist

- [ ] `JWT_SECRET_KEY` is set in Vercel environment variables
- [ ] Demo users are initialized on startup
- [ ] File paths use `/tmp` on Vercel
- [ ] Error logging is working
- [ ] Login endpoint has fallback user initialization

## If Still Failing

1. **Check Vercel Logs**:
   - Go to Vercel Dashboard → Your Project → Logs
   - Look for error messages with full traceback

2. **Check Environment Variables**:
   - Verify `JWT_SECRET_KEY` is set
   - Check it's not using default value

3. **Test Endpoint Directly**:
   ```bash
   curl -X POST https://your-app.vercel.app/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"patient@demo.com","password":"patient123"}' \
     -v
   ```

4. **Check File Permissions**:
   - `/tmp` should be writable
   - Files should be created successfully

## Current Status

✅ **Fixed Issues**:
- File path configuration for Vercel
- Demo user initialization on cold start
- Error handling and logging
- Fallback user creation in login endpoint

⚠️ **To Verify**:
- `JWT_SECRET_KEY` environment variable is set
- Vercel logs show successful initialization
- Login works after deployment

