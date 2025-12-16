# Production Debugging Guide

## ✅ All Changes Pushed

All fixes have been committed and pushed to the repository.

## 🔍 Common Production Issues & Solutions

### 1. **Environment Variables Not Set**
**Check**: Vercel Dashboard → Settings → Environment Variables

**Required Variables**:
```
JWT_SECRET_KEY=<your-secret-key>
GEMINI_API_KEY=<optional>
```

**Generate JWT Secret**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. **Cold Start Issue**
**Problem**: On Vercel, each serverless function starts fresh. Users file doesn't exist.

**Solution**: 
- ✅ Demo users are initialized on startup event
- ✅ Fallback initialization in login endpoint
- ✅ Users created automatically if file doesn't exist

### 3. **File Path Issues**
**Problem**: Writing to project root fails (read-only filesystem).

**Solution**:
- ✅ `users.json` → `/tmp/users.json` on Vercel
- ✅ `memory_bank.json` → `/tmp/memory_bank.json` on Vercel
- ✅ `uploads/` → `/tmp/uploads/` on Vercel

### 4. **JWT Token Creation Failure**
**Check**: If `JWT_SECRET_KEY` is not set or invalid.

**Solution**: Set proper `JWT_SECRET_KEY` in environment variables.

## 📋 What to Check in Deployment Logs

When you paste the deployment logs, look for:

1. **Startup Errors**:
   - "Failed to initialize demo users"
   - "Database initialization failed"
   - Any import errors

2. **Login/Register Errors**:
   - "Login failed for..."
   - "Registration failed for..."
   - Full traceback errors

3. **File System Errors**:
   - "Permission denied"
   - "No such file or directory"
   - "/tmp" related errors

4. **JWT Errors**:
   - "Invalid token"
   - "JWT_SECRET_KEY not set"

## 🔧 Quick Fixes to Try

### Fix 1: Verify Environment Variables
```bash
# In Vercel Dashboard → Settings → Environment Variables
# Make sure JWT_SECRET_KEY is set
```

### Fix 2: Check Vercel Logs
1. Go to Vercel Dashboard
2. Click on your project
3. Go to "Logs" tab
4. Look for errors during login/register requests

### Fix 3: Test API Directly
```bash
# Test login endpoint
curl -X POST https://your-app.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"patient@demo.com","password":"patient123"}' \
  -v

# Test register endpoint
curl -X POST https://your-app.vercel.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User","role":"patient"}' \
  -v
```

## 📝 Current Code Status

### Login Endpoint (`app/api_server.py`):
- ✅ Initializes demo users if none exist
- ✅ Fallback user creation on login attempt
- ✅ Comprehensive error logging
- ✅ JWT_SECRET_KEY validation

### Register Endpoint (`app/api_server.py`):
- ✅ Atomic file writes
- ✅ Error handling with traceback
- ✅ Proper error messages

### Auth Module (`app/auth.py`):
- ✅ Uses `/tmp/users.json` on Vercel
- ✅ Atomic file writes (temp file then rename)
- ✅ Graceful error handling
- ✅ Demo user initialization

### Startup Event (`app/api_server.py`):
- ✅ Initializes demo users on startup
- ✅ Database initialization
- ✅ Error logging

## 🚀 Next Steps

1. **Paste Deployment Logs**: Share the Vercel deployment logs
2. **Check Environment Variables**: Verify JWT_SECRET_KEY is set
3. **Test Endpoints**: Try curl commands above
4. **Check Vercel Logs**: Look for runtime errors

## 📊 Expected Behavior

**On Cold Start**:
1. App starts
2. Database initializes
3. Demo users are created in `/tmp/users.json`
4. Login/Register should work

**On Login**:
1. Check if users exist
2. If not, create demo users
3. Authenticate user
4. Create JWT token
5. Return response

**On Register**:
1. Validate input
2. Check if user exists
3. Create new user
4. Save to `/tmp/users.json`
5. Create JWT token
6. Return response

---

**Ready for debugging!** Paste the deployment logs and I'll help identify the issue.

