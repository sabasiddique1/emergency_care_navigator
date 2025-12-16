# Why Errors Only Happen in Production (Vercel) vs Local

## Key Differences

### Local Environment:
1. **Persistent Process**: Server runs continuously
2. **Startup Event Runs**: `@app.on_event("startup")` executes once when server starts
3. **Database Persists**: SQLite file exists between requests
4. **Warm State**: Database already initialized, users already exist

### Production (Vercel):
1. **Serverless Functions**: Each request can be a cold start
2. **Startup Event May Not Run**: On cold starts, startup event might not execute before first request
3. **Database Resets**: `/tmp/emergencycare.db` might not exist on cold start
4. **Cold State**: Database not initialized, tables don't exist, users don't exist

## The Problem:

**On Vercel Cold Start:**
1. Function starts fresh
2. Login endpoint is called
3. Database not initialized yet (startup event hasn't run)
4. Query fails: "no such table: users"
5. 500 error

**Locally:**
1. Server starts once
2. Startup event runs immediately
3. Database initialized
4. Users created
5. All requests work

## Solution:

We need to ensure database initialization happens **synchronously** before any database queries, not just in the startup event.

