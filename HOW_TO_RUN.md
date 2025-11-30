# 🚑 How to Run EmergencyCareNavigator - Complete Guide

## ✅ Current Status

**The app is now running!** 

- **URL**: http://localhost:8000
- **Mode**: MockLLM (no Gemini API key needed - fully functional!)
- **Status**: ✅ Ready to use

## 🎯 Quick Start (3 Steps)

### 1. Open in Browser
```
http://localhost:8000
```

### 2. Fill Out the Form
- **Patient Name**: (optional, defaults to "Anonymous")
- **Location**: e.g., "Karachi Pakistan" or "New York, USA"
- **Symptoms**: Comma-separated, e.g., "chest pain, difficulty breathing"
- **Red Flags**: Check all that apply

### 3. Click "Get Recommendations"

You'll get:
- ✅ Triage level (emergency/high/medium/low)
- ✅ Top 5 nearby facilities with ETA and distance
- ✅ SBAR handoff packet
- ✅ Booking approval (if urgent)

## 🎤 Voice Input Feature

1. Click the **🎤 Voice Input** button
2. Grant microphone permission when prompted
3. Speak your symptoms clearly
4. The text will automatically fill in

**Note**: Works best in Chrome/Edge browsers

## 🔧 Running the App Yourself

### Option 1: Use the Script (Easiest)

**Mac/Linux:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

### Option 2: Manual Start

```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate     # Windows

# Start server
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Python Direct

```bash
source venv/bin/activate
python -m app.api_server
```

## 🤖 Gemini API Key (Optional)

### Current Status: **MockLLM Mode** ✅

The app works **perfectly** without Gemini! The triage logic is rule-based and deterministic.

### If You Want Gemini (Optional):

1. **Get API Key**: https://aistudio.google.com/app/apikey
2. **Set Environment Variable**:
   ```bash
   export GEMINI_API_KEY="your-key-here"  # Mac/Linux
   set GEMINI_API_KEY=your-key-here       # Windows
   ```
3. **Restart the server**

**What Gemini Adds:**
- More natural, empathetic explanations in triage results
- Better user-facing messages
- **Note**: Core triage logic stays rule-based for safety

See `GEMINI_SETUP.md` for detailed instructions.

## 📊 What the App Does

### Multi-Agent System
1. **IntakeAgent**: Collects emergency questionnaire
2. **TriageAgent**: Rule-based triage (emergency/high/medium/low)
3. **FacilityFinderAgent**: Finds nearby hospitals/clinics
4. **CoordinatorAgent**: Orchestrates workflow, generates handoff packet

### External Tools
- **Nominatim**: Geocoding (location → lat/lon)
- **OSRM**: Routing (ETA calculations)
- **Graceful Fallback**: If OSRM fails, uses distance-only ranking

### Features
- ✅ Real-time facility search
- ✅ ETA calculations
- ✅ SBAR handoff packet (clinician-ready)
- ✅ Booking workflow (simulated)
- ✅ Memory persistence (preferred city, last facility)
- ✅ Structured logging (check console)

## 🐛 Troubleshooting

### Port 8000 Already in Use?
```bash
uvicorn app.api_server:app --port 8001
```
Then open: http://localhost:8001

### Geocoding Fails?
- Try more specific location: "City, Country"
- Check internet connection
- Wait a moment (rate limits apply)

### Voice Input Not Working?
- Grant microphone permissions
- Use Chrome/Edge browser
- Check browser console (F12) for errors

### Server Won't Start?
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

## 📝 Example Test Cases

### Emergency Case
- **Location**: "Karachi Pakistan"
- **Symptoms**: "chest pain, sweating"
- **Red Flags**: ✅ Chest pain
- **Expected**: Emergency level, hospital prioritized

### Low Urgency Case
- **Location**: "Karachi Pakistan"
- **Symptoms**: "mild fever, cough"
- **Red Flags**: None
- **Expected**: Low level, clinic prioritized

## 🔍 Observability

Check the terminal/console for:
- Tool calls (geocode, facility search, ETA)
- Agent actions
- Errors and retries
- Metrics (tool_calls, llm_calls, errors)

## 🎯 Next Steps

1. **Test the app**: Open http://localhost:8000
2. **Try different scenarios**: Emergency vs. low urgency
3. **Test voice input**: Click the microphone button
4. **Review handoff packets**: See SBAR format output
5. **Check console logs**: See observability in action

## 📚 Files Reference

- `app/api_server.py` - FastAPI server
- `app/agents.py` - Multi-agent system
- `app/tools.py` - External API tools
- `static/index.html` - Frontend UI
- `README_APP.md` - Full documentation
- `GEMINI_SETUP.md` - Gemini API setup guide

---

**The app is running and ready to use!** 🎉

Open http://localhost:8000 in your browser to get started.

