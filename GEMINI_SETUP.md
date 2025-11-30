# Gemini API Key Setup (Optional)

## Why Gemini?

The app works **perfectly fine without Gemini** using MockLLM mode. However, if you want:
- **More empathetic, natural language explanations** in triage results
- **Better user-facing messages** (the core triage logic is still rule-based for safety)

Then you can add a Gemini API key.

## How to Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

## How to Set the API Key

### Option 1: Environment Variable (Recommended)

**Mac/Linux:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

### Option 2: Add to run script

Edit `run.sh` (Mac/Linux) or `run.bat` (Windows) and add:
```bash
export GEMINI_API_KEY="your-api-key-here"  # Add this line
```

### Option 3: Create .env file (Advanced)

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your-api-key-here
```

Then install python-dotenv and load it in the app (not currently implemented, but easy to add).

## Verify It's Working

1. Start the app
2. Check the console output - you should see:
   ```
   [LOG] {'ts': '...', 'trace_id': '...', 'event': 'llm_ready', 'provider': 'gemini'}
   ```
   Instead of:
   ```
   [LOG] {'ts': '...', 'trace_id': '...', 'event': 'llm_ready', 'provider': 'mock'}
   ```

## What Works Without Gemini?

✅ **Everything!** The app is fully functional:
- Triage logic (rule-based, deterministic)
- Facility search and ranking
- ETA calculations
- Handoff packet generation
- Booking workflow

The only difference is the **explanation text** in triage results will be more generic.

## Cost

- Gemini 1.5 Flash is **free** for reasonable usage
- Very cost-effective (pennies per request)
- No credit card required for basic usage

## Security Note

⚠️ **Never commit your API key to git!**

Add to `.gitignore`:
```
.env
*.key
```

