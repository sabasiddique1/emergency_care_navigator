# EmergencyCareNavigator - Full Stack App

Run the EmergencyCareNavigator as a local web application with a beautiful frontend.

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. (Optional) Set Gemini API Key

For LLM-powered explanations, set the environment variable:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

If not set, the app will use MockLLM mode (still fully functional).

### 3. Run the Server

```bash
python -m app.api_server
```

Or using uvicorn directly:

```bash
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open in Browser

Navigate to: **http://localhost:8000**

## Features

### Frontend
- ✅ Beautiful, modern UI with gradient design
- ✅ Voice input via Web Speech API (browser-based)
- ✅ Real-time form validation
- ✅ Responsive design
- ✅ Clear triage level indicators (color-coded)
- ✅ Facility recommendations with ETA/distance
- ✅ SBAR-style handoff packet display
- ✅ Booking approval workflow

### Backend
- ✅ FastAPI REST API
- ✅ Multi-agent system (Triage, FacilityFinder, Coordinator)
- ✅ External API integration (Nominatim, OSRM)
- ✅ Session management for booking state
- ✅ Memory persistence (JSON file)
- ✅ Structured logging and observability
- ✅ Error handling with retry logic

## API Endpoints

- `GET /` - Serve frontend
- `POST /api/intake` - Process emergency intake
- `POST /api/booking/approve/{session_id}` - Approve booking
- `GET /api/health` - Health check

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── models.py          # Pydantic data models
│   ├── observability.py   # Logging, tracing, metrics
│   ├── llm_client.py      # LLM wrapper (Gemini/Mock)
│   ├── tools.py           # External API tools
│   ├── memory.py          # Memory management
│   ├── agents.py          # Multi-agent system
│   └── api_server.py      # FastAPI server
├── static/
│   └── index.html         # Frontend UI
├── requirements.txt
└── README_APP.md
```

## Usage Example

1. Fill out the intake form:
   - Patient name (optional)
   - Location (e.g., "Karachi Pakistan")
   - Symptoms (comma-separated or use voice input)
   - Check red flags if applicable

2. Click "Get Recommendations"

3. View results:
   - Triage level (emergency/high/medium/low)
   - Top 5 nearby facilities with ETA
   - SBAR handoff packet

4. If urgent, approve booking (simulated)

## Voice Input

Click the "🎤 Voice Input" button to use your browser's speech recognition:
- Supported in Chrome, Edge, Safari
- Speaks your symptoms
- Automatically fills the symptoms field
- Note: Requires microphone permission

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
uvicorn app.api_server:app --port 8001
```

### Geocoding Fails
- Try a more specific location (e.g., "City, Country")
- Check internet connection
- Nominatim has rate limits (wait a moment and retry)

### OSRM ETA Unavailable
- System automatically falls back to distance-only ranking
- This is normal if OSRM service is down

### Voice Input Not Working
- Ensure microphone permissions are granted
- Use Chrome/Edge for best compatibility
- Check browser console for errors

## Development

### Run with Auto-reload
```bash
uvicorn app.api_server:app --reload
```

### Check Logs
The server prints structured logs to console:
- Tool calls
- Agent actions
- Errors and retries
- Metrics (tool_calls, llm_calls, errors)

## Notes

- The notebook version (`emergencycarenavigator-agent-capstone.ipynb`) remains unchanged and can still be used in Kaggle
- This app uses the same core logic extracted from the notebook
- Memory is stored in `memory_bank.json` in the project root
- Sessions are stored in-memory (restart clears them)

## Next Steps

- Add database for session persistence
- Add authentication/authorization
- Deploy to cloud (Heroku, Railway, etc.)
- Add more facility filters (specialties, availability)
- Integrate with real hospital booking systems

