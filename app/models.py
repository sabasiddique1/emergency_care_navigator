"""Data models for EmergencyCareNavigator."""
from typing import List, Optional
from pydantic import BaseModel, Field


class IntakeAnswers(BaseModel):
    name: str = Field(default="Anonymous")
    age_years: Optional[int] = None
    sex: Optional[str] = None  # 'M','F','Other'
    location_query: str = Field(..., description="User-provided location text")
    symptoms: List[str] = Field(default_factory=list)
    duration_minutes: Optional[int] = None

    # Red flags
    unconscious: bool = False
    breathing_difficulty: bool = False
    chest_pain: bool = False
    stroke_signs: bool = False
    major_bleeding: bool = False
    severe_allergy: bool = False
    pregnancy: bool = False
    injury_trauma: bool = False


class TriageResult(BaseModel):
    level: str  # "emergency"|"high"|"medium"|"low"
    reason: str
    recommended_action: str
    safety_note: str


class Facility(BaseModel):
    name: str
    address: str
    lat: float
    lon: float
    kind: str  # hospital/clinic/pharmacy
    distance_km: Optional[float] = None
    eta_minutes: Optional[int] = None
    source: str = "OSM"


class BookingState(BaseModel):
    status: str = "not_started"  # not_started | pending_approval | confirmed | failed | skipped
    facility_name: Optional[str] = None
    requested_at: Optional[str] = None
    approved_at: Optional[str] = None
    note: Optional[str] = None


class Recommendation(BaseModel):
    triage: TriageResult
    top_choices: List[Facility]
    route_notes: str
    handoff_packet: str
    booking_status: str  # "not_started"|"pending_approval"|"confirmed"|"skipped"
    booking: Optional[BookingState] = None


class MemoryBank(BaseModel):
    preferred_city: Optional[str] = None
    last_facility_used: Optional[str] = None

