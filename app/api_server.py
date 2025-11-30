"""FastAPI server for EmergencyCareNavigator."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, Any
import uuid

from app.models import IntakeAnswers, Recommendation, BookingState
from app.agents import CoordinatorAgent
from app.observability import log_event

app = FastAPI(title="EmergencyCareNavigator API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store coordinator instances per session
sessions: Dict[str, CoordinatorAgent] = {}


@app.get("/")
async def root():
    """Serve the frontend."""
    return FileResponse("static/index.html")


@app.post("/api/intake")
async def process_intake(intake: IntakeAnswers):
    """Process emergency intake and return recommendations."""
    session_id = str(uuid.uuid4())
    coordinator = CoordinatorAgent()
    sessions[session_id] = coordinator
    
    try:
        result = coordinator.run(intake)
        result_dict = result.model_dump()
        result_dict["session_id"] = session_id  # Include session ID for booking approval
        result_dict["booking"] = coordinator.booking.model_dump() if result.booking_status != "skipped" else None
        return result_dict
    except Exception as e:
        log_event("api_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/booking/approve/{session_id}")
async def approve_booking(session_id: str) -> BookingState:
    """Approve pending booking for a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    coordinator = sessions[session_id]
    booking = coordinator.approve_booking()
    return booking


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "EmergencyCareNavigator"}


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

