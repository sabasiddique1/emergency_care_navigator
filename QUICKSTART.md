# 🚑 EmergencyCareNavigator - Quick Start Guide

## Run the Full-Stack App in 3 Steps

### Step 1: Install Dependencies

**Mac/Linux:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

**Manual:**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: (Optional) Set Gemini API Key

For LLM-powered explanations:
```bash
export GEMINI_API_KEY="your-key-here"  # Mac/Linux
set GEMINI_API_KEY=your-key-here       # Windows
```

If not set, the app runs in MockLLM mode (still fully functional).

### Step 3: Start the Server

**Using the script:**
```bash
./run.sh  # Mac/Linux
run.bat   # Windows
```

**Or manually:**
```bash
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Open in Browser

Navigate to: **http://localhost:8000**

## What You'll See

1. **Intake Form**: Fill out patient info, location, symptoms, and red flags
2. **Voice Input**: Click 🎤 to use speech recognition (Chrome/Edge recommended)
3. **Results**: 
   - Triage level (color-coded: emergency/high/medium/low)
   - Top 5 nearby facilities with ETA and distance
   - SBAR handoff packet
   - Booking approval (if urgent)

## Features

✅ **Beautiful UI** - Modern gradient design, responsive layout  
✅ **Voice Input** - Web Speech API for hands-free symptom entry  
✅ **Real-time Processing** - Fast geocoding and facility search  
✅ **Multi-Agent System** - Triage, FacilityFinder, Coordinator agents  
✅ **External APIs** - Nominatim (geocoding) + OSRM (routing)  
✅ **Session Management** - Booking state persistence  
✅ **Error Handling** - Graceful fallbacks and retry logic  

## Troubleshooting

**Port 8000 in use?**
```bash
uvicorn app.api_server:app --port 8001
```

**Geocoding fails?**
- Try more specific location: "City, Country"
- Check internet connection
- Wait a moment (rate limits)

**Voice input not working?**
- Grant microphone permissions
- Use Chrome/Edge browser
- Check browser console for errors

## Project Structure

```
.
├── app/              # Backend Python modules
│   ├── models.py     # Data models
│   ├── agents.py     # Multi-agent system
│   ├── tools.py       # External API tools
│   └── api_server.py # FastAPI server
├── static/           # Frontend
│   └── index.html    # Web UI
└── requirements.txt  # Dependencies
```

## Next Steps

- Try different locations and symptoms
- Test voice input with your microphone
- Check the console logs for observability
- Review the handoff packet format

Enjoy! 🎉

