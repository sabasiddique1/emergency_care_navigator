#!/usr/bin/env python3
"""
EmergencyCareNavigator — Multi-Agent Emergency Routing & Handoff Assistant
Standalone Python version extracted from Kaggle notebook

This is a self-contained demonstration script.
It does NOT use the app/ code - it is a standalone implementation.

To run:
  1. Install dependencies: pip install requests pydantic rich google-generativeai
  2. Set GEMINI_API_KEY environment variable (optional)
  3. Run: python emergencycarenavigator_standalone.py
"""

# Note: This file is extracted from the Kaggle notebook.
# The app/ directory contains a separate FastAPI implementation.
# They share similar concepts but are independent codebases.

# =========================================
# 1) Install & Imports
# =========================================
# NOTE: Keep installs minimal for Kaggle runtime.


import os, json, time, math, uuid, random, datetime
from typing import List, Optional, Dict, Any, Tuple
import requests
from pydantic import BaseModel, Field
from rich import print as rprint


# =========================================
# Load Kaggle secrets safely
# =========================================
GEMINI_API_KEY = None
try:
    from kaggle_secrets import UserSecretsClient
    user_secrets = UserSecretsClient()
    GEMINI_API_KEY = user_secrets.get_secret("GEMINI_API_KEY")
except Exception:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

USE_GEMINI = bool(GEMINI_API_KEY)

rprint({
    "USE_GEMINI": USE_GEMINI,
    "hint": "If USE_GEMINI=False, add a Kaggle secret GEMINI_API_KEY (optional)."
})


# =========================================
# 3) Simple Observability (Logs/Traces/Metrics-lite)
# =========================================

TRACE_ID = str(uuid.uuid4())

def now_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def log_event(event: str, **fields):
    payload = {"ts": now_iso(), "trace_id": TRACE_ID, "event": event, **fields}
    rprint(payload)
    return payload

METRICS = {"tool_calls": 0, "llm_calls": 0, "errors": 0}

log_event("boot", metrics=METRICS)


# =========================================
# 4) LLM wrapper: Gemini or Mock
# =========================================
class LLMClient:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class MockLLM(LLMClient):
    def generate(self, prompt: str) -> str:
        # Deterministic-ish, safe fallback.
        return (
            "I'm running in MOCK mode (no API key).\n"
            "Summary: Based on provided symptoms, prioritize safety. "
            "If severe symptoms are present (breathing trouble, chest pain, stroke signs, major bleeding, unconsciousness), seek emergency care immediately."
        )

class GeminiLLM(LLMClient):
    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")  # fast & cost-friendly
    def generate(self, prompt: str) -> str:
        METRICS["llm_calls"] += 1
        resp = self.model.generate_content(prompt)
        return resp.text

llm: LLMClient = GeminiLLM(GEMINI_API_KEY) if USE_GEMINI else MockLLM()
log_event("llm_ready", provider=("gemini" if USE_GEMINI else "mock"), metrics=METRICS)


# =========================================
# 5) Schemas
# =========================================
class IntakeAnswers(BaseModel):
    name: str = Field(default="Anonymous")
    age_years: Optional[int] = None
    sex: Optional[str] = None  # 'M','F','Other'
    location_query: str = Field(..., description="User-provided location text, e.g., 'Gulshan-e-Iqbal Karachi'")
    symptoms: List[str] = Field(default_factory=list)
    duration_minutes: Optional[int] = None

    # Red flags
    unconscious: bool = False
    breathing_difficulty: bool = False
    chest_pain: bool = False
    stroke_signs: bool = False  # face droop, arm weakness, speech problems
    major_bleeding: bool = False
    severe_allergy: bool = False
    pregnancy: bool = False
    injury_trauma: bool = False

class TriageLevel(str):
    # kept as string-like for readability
    pass

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

class Recommendation(BaseModel):
    triage: TriageResult
    top_choices: List[Facility]
    route_notes: str
    handoff_packet: str
    booking_status: str  # "not_started"|"pending_approval"|"confirmed"|"skipped"


# =========================================
# 6A) Tool: Geocode (Nominatim) with retry
# =========================================
NOMINATIM = "https://nominatim.openstreetmap.org/search"
OSRM_ROUTE = "https://router.project-osrm.org/route/v1/driving"

HEADERS = {
    "User-Agent": "EmergencyCareNavigator/1.0 (capstone; kaggle notebook)"
}

def tool_geocode(query: str, max_retries: int = 2) -> Tuple[float, float, str]:
    """Geocode location query with retry logic and friendly error messages."""
    METRICS["tool_calls"] += 1
    log_event("tool_call", tool="geocode", query=query)
    params = {"q": query, "format": "json", "limit": 1}
    
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            r = requests.get(NOMINATIM, params=params, headers=HEADERS, timeout=20)
            r.raise_for_status()
            data = r.json()
            if not data:
                raise ValueError(f"No geocode results for: {query}")
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            display = data[0].get("display_name", query)
            return lat, lon, display
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(1.0 * (attempt + 1))  # Simple backoff
                log_event("tool_retry", tool="geocode", attempt=attempt+1, error=str(e))
            else:
                METRICS["errors"] += 1
                log_event("tool_error", tool="geocode", error=str(e), final=True)
        except (ValueError, KeyError, IndexError) as e:
            last_error = e
            METRICS["errors"] += 1
            log_event("tool_error", tool="geocode", error=str(e))
            break
    
    # Friendly error message
    raise ValueError(
        f"Could not geocode location '{query}'. "
        f"Please try a more specific location (e.g., 'City, Country' or a well-known landmark). "
        f"Error: {last_error}"
    )


# =========================================
# 6B) Tool: Nearby facilities (Nominatim search) with retry
# =========================================
def tool_find_facilities(lat: float, lon: float, query: str, kind: str, limit: int = 7, max_retries: int = 2) -> List[Facility]:
    """Use Nominatim search around a coordinate (bounded search) with retry logic."""
    METRICS["tool_calls"] += 1
    log_event("tool_call", tool="find_facilities", kind=kind, query=query, lat=lat, lon=lon)
    params = {
        "q": query,
        "format": "json",
        "limit": limit,
        "viewbox": f"{lon-0.15},{lat+0.15},{lon+0.15},{lat-0.15}",  # rough box (~15km depending latitude)
        "bounded": 1
    }
    
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            r = requests.get(NOMINATIM, params=params, headers=HEADERS, timeout=20)
            r.raise_for_status()
            data = r.json() or []
            facilities = []
            for item in data:
                name = item.get("display_name", "Unknown")
                facilities.append(Facility(
                    name=name.split(",")[0],
                    address=name,
                    lat=float(item["lat"]),
                    lon=float(item["lon"]),
                    kind=kind,
                    source="OSM/Nominatim"
                ))
            return facilities
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(1.0 * (attempt + 1))
                log_event("tool_retry", tool="find_facilities", attempt=attempt+1, error=str(e))
            else:
                METRICS["errors"] += 1
                log_event("tool_error", tool="find_facilities", error=str(e), final=True)
                return []  # Return empty list on failure
        except (ValueError, KeyError) as e:
            last_error = e
            METRICS["errors"] += 1
            log_event("tool_error", tool="find_facilities", error=str(e))
            return []
    
    return []  # Fallback


# =========================================
# 6C) Tool: Route ETA (OSRM) with graceful fallback
# =========================================
def tool_eta_minutes(origin: Tuple[float,float], dest: Tuple[float,float], max_retries: int = 1) -> Optional[int]:
    """Get ETA from OSRM. Returns None if OSRM fails (caller should fallback to distance-only ranking)."""
    METRICS["tool_calls"] += 1
    (olat, olon) = origin
    (dlat, dlon) = dest
    log_event("tool_call", tool="eta", origin=origin, dest=dest)
    url = f"{OSRM_ROUTE}/{olon},{olat};{dlon},{dlat}"
    params = {"overview": "false"}
    
    for attempt in range(max_retries + 1):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                if attempt < max_retries:
                    time.sleep(0.5)
                    continue
                log_event("tool_warn", tool="eta", status=r.status_code, note="OSRM failed, will use distance-only ranking")
                return None
            data = r.json()
            routes = data.get("routes") or []
            if not routes:
                log_event("tool_warn", tool="eta", note="No routes from OSRM, will use distance-only ranking")
                return None
            seconds = routes[0].get("duration")
            if seconds is None:
                log_event("tool_warn", tool="eta", note="No duration in OSRM response, will use distance-only ranking")
                return None
            return int(round(seconds / 60))
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                time.sleep(0.5)
                log_event("tool_retry", tool="eta", attempt=attempt+1, error=str(e))
            else:
                METRICS["errors"] += 1
                log_event("tool_error", tool="eta", error=str(e), note="OSRM failed, will use distance-only ranking")
                return None
    
    return None


# =========================================
# 6D) Tool: Simulated long-running booking (pause/resume)
# =========================================
class BookingState(BaseModel):
    status: str = "not_started"   # not_started | pending_approval | confirmed | failed | skipped
    facility_name: Optional[str] = None
    requested_at: Optional[str] = None
    approved_at: Optional[str] = None
    note: Optional[str] = None

def tool_request_booking(state: BookingState, facility: Facility) -> BookingState:
    METRICS["tool_calls"] += 1
    log_event("tool_call", tool="request_booking", facility=facility.name)
    state.status = "pending_approval"
    state.facility_name = facility.name
    state.requested_at = now_iso()
    state.note = "Simulated booking request created. Requires human approval to continue."
    return state

def tool_approve_booking(state: BookingState) -> BookingState:
    METRICS["tool_calls"] += 1
    log_event("tool_call", tool="approve_booking", facility=state.facility_name)
    if state.status != "pending_approval":
        state.note = f"Cannot approve from status={state.status}"
        return state
    state.status = "confirmed"
    state.approved_at = now_iso()
    state.note = "Simulated booking confirmed."
    return state


# =========================================
# 7) Session & Memory (very small)
# =========================================
MEM_PATH = "memory_bank.json"

class MemoryBank(BaseModel):
    preferred_city: Optional[str] = None
    last_facility_used: Optional[str] = None

def load_memory() -> MemoryBank:
    if not os.path.exists(MEM_PATH):
        return MemoryBank()
    try:
        return MemoryBank(**json.load(open(MEM_PATH, "r", encoding="utf-8")))
    except Exception:
        return MemoryBank()

def save_memory(mem: MemoryBank):
    with open(MEM_PATH, "w", encoding="utf-8") as f:
        json.dump(mem.model_dump(), f, indent=2)

memory = load_memory()
log_event("memory_loaded", memory=memory.model_dump())


# =========================================
# 8) Agents
# =========================================
class IntakeAgent:
    def run(self) -> IntakeAnswers:
        rprint("\n[bold]Emergency Intake (fast)[/bold]")
        name = input("Patient name (or 'Anonymous'): ").strip() or "Anonymous"
        loc = input("Current location (area/city): ").strip()
        symptoms_raw = input("Main symptoms (comma-separated): ").strip()
        symptoms = [s.strip() for s in symptoms_raw.split(",") if s.strip()]

        def yn(q): 
            return (input(q + " (y/n): ").strip().lower()[:1] == "y")

        ans = IntakeAnswers(
            name=name,
            location_query=loc,
            symptoms=symptoms,
            unconscious=yn("Unconscious / not responding?"),
            breathing_difficulty=yn("Difficulty breathing?"),
            chest_pain=yn("Chest pain/pressure?"),
            stroke_signs=yn("Stroke signs (face droop/arm weakness/speech trouble)?"),
            major_bleeding=yn("Major bleeding that won't stop?"),
            severe_allergy=yn("Severe allergy/anaphylaxis signs?"),
            injury_trauma=yn("Injury/trauma (accident/fall)?"),
            pregnancy=yn("Pregnant?"),
        )
        return ans

class TriageAgent:
    def run(self, intake: IntakeAnswers) -> TriageResult:
        # Conservative escalation rules
        red_flags = [
            intake.unconscious,
            intake.breathing_difficulty,
            intake.chest_pain,
            intake.stroke_signs,
            intake.major_bleeding,
            intake.severe_allergy
        ]
        if any(red_flags):
            level = "emergency"
            reason = "One or more red-flag symptoms present (airway/breathing/circulation/neurologic risk)."
            action = "🚨 CALL EMERGENCY SERVICES (911/ambulance) NOW. Do not delay. Prefer ambulance/ER."
        elif intake.injury_trauma:
            level = "high"
            reason = "Trauma/injury reported without immediate red flags."
            action = "Seek urgent medical evaluation immediately. Consider ER/urgent care. If symptoms worsen, call emergency services."
        else:
            # very rough heuristic for demo
            level = "medium" if len(intake.symptoms) >= 2 else "low"
            reason = "No immediate red flags reported."
            action = "If symptoms worsen or new red flags appear, escalate to emergency care."

        safety = (
            "⚠️ IMPORTANT: This tool does NOT diagnose. "
            "If you're unsure, treat it as urgent. "
            "For emergencies, call local emergency services (911/ambulance) immediately."
        )

        # Optional LLM to convert into calm human language
        explanation = ""
        try:
            prompt = f"""You are a safety-focused emergency navigation assistant.
Return a short, calm explanation and next steps in plain language.
Do NOT diagnose. Always include a safety reminder.
Inputs:
- Symptoms: {intake.symptoms}
- Flags: unconscious={intake.unconscious}, breathing_difficulty={intake.breathing_difficulty}, chest_pain={intake.chest_pain}, stroke_signs={intake.stroke_signs}, major_bleeding={intake.major_bleeding}, severe_allergy={intake.severe_allergy}, trauma={intake.injury_trauma}
- Chosen Level: {level}
"""
            explanation = llm.generate(prompt).strip()
        except Exception as e:
            METRICS["errors"] += 1
            explanation = ""
            log_event("llm_error", where="TriageAgent", error=str(e))

        final_reason = reason + ("\n\nLLM Explanation:\n" + explanation if explanation else "")
        return TriageResult(level=level, reason=final_reason, recommended_action=action, safety_note=safety)

class FacilityFinderAgent:
    def run(self, origin_lat: float, origin_lon: float, triage_level: str) -> List[Facility]:
        # For emergency/high -> prioritize hospitals; otherwise clinics
        if triage_level in ("emergency","high"):
            kinds = [("hospital", "hospital"), ("clinic", "clinic")]
            search_terms = ["hospital", "emergency hospital", "ER", "clinic"]
        else:
            kinds = [("clinic", "clinic"), ("hospital", "hospital")]
            search_terms = ["clinic", "hospital"]

        # Collect candidates
        candidates: List[Facility] = []
        for term in search_terms:
            for kind, klabel in kinds:
                try:
                    res = tool_find_facilities(origin_lat, origin_lon, term, klabel, limit=6)
                    candidates.extend(res)
                except Exception as e:
                    METRICS["errors"] += 1
                    log_event("tool_error", tool="find_facilities", error=str(e), term=term, kind=klabel)

        # De-dup by name+rounded coords (more robust)
        uniq = {}
        for f in candidates:
            # Normalize name: lowercase, strip, take first meaningful part
            name_normalized = f.name.lower().strip().split(",")[0].strip()
            # Round coords to ~100m precision for de-dup
            key = (name_normalized, round(f.lat, 3), round(f.lon, 3))
            # Keep the first occurrence (or prefer hospital over clinic if same location)
            if key not in uniq or (f.kind == "hospital" and uniq[key].kind != "hospital"):
                uniq[key] = f
        facilities = list(uniq.values())

        # Compute distances + ETA
        def haversine_km(lat1, lon1, lat2, lon2):
            R = 6371.0
            p = math.pi/180
            dlat = (lat2-lat1)*p
            dlon = (lon2-lon1)*p
            a = math.sin(dlat/2)**2 + math.cos(lat1*p)*math.cos(lat2*p)*math.sin(dlon/2)**2
            return 2*R*math.asin(math.sqrt(a))

        origin = (origin_lat, origin_lon)
        for f in facilities:
            f.distance_km = round(haversine_km(origin_lat, origin_lon, f.lat, f.lon), 2)
            eta = None
            try:
                eta = tool_eta_minutes(origin, (f.lat, f.lon))
            except Exception as e:
                METRICS["errors"] += 1
                log_event("tool_error", tool="eta", error=str(e))
            f.eta_minutes = eta

        # Rank: ETA first if available, else distance only (graceful fallback if OSRM fails)
        facilities.sort(key=lambda x: (
            x.eta_minutes if x.eta_minutes is not None else 9999,
            x.distance_km if x.distance_km is not None else 9999
        ))
        return facilities[:5]

class CoordinatorAgent:
    def __init__(self):
        self.booking = BookingState()

    def build_handoff_packet(self, intake: IntakeAnswers, triage: TriageResult, chosen: Facility, eta: Optional[int]) -> str:
        # SBAR-ish format (simple)
        s = []
        s.append(f"S (Situation): Patient '{intake.name}' en route. Triage level: {triage.level}." )
        s.append(f"B (Background): Symptoms: {', '.join(intake.symptoms) if intake.symptoms else 'N/A'}." )
        flags = []
        for k in ["unconscious","breathing_difficulty","chest_pain","stroke_signs","major_bleeding","severe_allergy","injury_trauma","pregnancy"]:
            if getattr(intake, k):
                flags.append(k)
        s.append(f"A (Assessment): Flags: {', '.join(flags) if flags else 'None reported'}." )
        s.append(f"R (Recommendation): Prepare triage on arrival. Estimated arrival: {eta if eta is not None else 'unknown'} min." )
        s.append("Note: This summary is generated for information support only; clinician judgement required.")
        s.append(f"Destination: {chosen.name} ({chosen.address})")
        return "\n".join(s)

    def run(self, intake: IntakeAnswers) -> Recommendation:
        log_event("coordinator_start", intake=intake.model_dump())

        # 1) Geocode
        try:
            lat, lon, disp = tool_geocode(intake.location_query)
        except Exception as e:
            METRICS["errors"] += 1
            log_event("tool_error", tool="geocode", error=str(e))
            raise

        # 2) Triage
        triage = TriageAgent().run(intake)

        # 3) Find facilities
        facilities = FacilityFinderAgent().run(lat, lon, triage.level)
        if not facilities:
            raise RuntimeError("No facilities found. Try a broader location query.")

        chosen = facilities[0]
        eta = chosen.eta_minutes

        # 4) Route notes
        route_notes = (
            f"Nearest recommended: {chosen.name}. Estimated travel time: {eta if eta is not None else 'unknown'} min. " 
            "If traffic is heavy or symptoms worsen, consider calling emergency services."
        )

        # 5) Handoff packet
        handoff = self.build_handoff_packet(intake, triage, chosen, eta)

        # 6) Booking (simulated long-running operation)
        booking_status = "skipped"
        if triage.level in ("emergency", "high"):
            self.booking = tool_request_booking(self.booking, chosen)
            booking_status = self.booking.status

        # 7) Update memory
        mem = memory
        mem.preferred_city = intake.location_query
        mem.last_facility_used = chosen.name
        save_memory(mem)

        log_event("coordinator_done", chosen=chosen.model_dump(), booking=self.booking.model_dump(), metrics=METRICS)

        return Recommendation(
            triage=triage,
            top_choices=facilities,
            route_notes=route_notes,
            handoff_packet=handoff,
            booking_status=booking_status
        )


def run_demo():
    """Interactive demo: collects intake, runs coordinator, shows results, handles booking approval."""
    intake = IntakeAgent().run()
    c = CoordinatorAgent()  # Create coordinator ONCE and reuse it
    rec = c.run(intake)

    rprint("\n[bold cyan]=== TRIAGE RESULT ===[/bold cyan]")
    rprint(rec.triage.model_dump())
    
    # Safety warning for emergencies
    if rec.triage.level in ("emergency", "high"):
        rprint("\n[bold red]⚠️  URGENT: Call emergency services (911/ambulance) immediately if not already done![/bold red]")

    rprint("\n[bold cyan]=== TOP FACILITIES ===[/bold cyan]")
    for i, f in enumerate(rec.top_choices, 1):
        eta_str = f"{f.eta_minutes} min" if f.eta_minutes is not None else "unknown (using distance)"
        rprint(f"{i}) {f.name} | kind={f.kind} | eta={eta_str} | dist={f.distance_km} km")
        rprint(f"    {f.address}")

    rprint("\n[bold cyan]=== ROUTE NOTES ===[/bold cyan]")
    rprint(rec.route_notes)

    rprint("\n[bold cyan]=== HANDOFF PACKET ===[/bold cyan]")
    rprint(rec.handoff_packet)

    rprint("\n[bold cyan]=== BOOKING ===[/bold cyan]")
    rprint(rec.booking_status)
    if rec.booking_status == "pending_approval":
        rprint("\n[yellow]Booking is pending approval (long-running operation).[/yellow]")
        approve = input("Approve booking now? (y/n): ").strip().lower().startswith("y")
        if approve:
            # FIXED: Use the SAME coordinator instance's booking state
            c.booking = tool_approve_booking(c.booking)
            rprint("\n[green]Booking approved![/green]")
            rprint(c.booking.model_dump())
        else:
            rprint("Skipped approval.")
            c.booking.status = "skipped"
            c.booking.note = "User skipped booking approval."

# --- RUN ---
run_demo()


# =========================================
# Evaluation: Automated test scenarios (rule-based, no external API calls)
# =========================================
TESTS = [
    {
        "name": "Severe chest pain (emergency)",
        "intake": IntakeAnswers(
            name="Test Patient",
            location_query="Karachi Pakistan",
            symptoms=["chest pain", "sweating", "nausea"],
            chest_pain=True,
            breathing_difficulty=False
        ),
        "expect_level": "emergency"
    },
    {
        "name": "Stroke signs (emergency)",
        "intake": IntakeAnswers(
            name="Test Patient",
            location_query="Lahore Pakistan",
            symptoms=["face drooping", "arm weakness", "speech difficulty"],
            stroke_signs=True,
            chest_pain=False
        ),
        "expect_level": "emergency"
    },
    {
        "name": "Anaphylaxis/severe allergy (emergency)",
        "intake": IntakeAnswers(
            name="Test Patient",
            location_query="Islamabad Pakistan",
            symptoms=["hives", "swelling", "difficulty breathing"],
            severe_allergy=True,
            breathing_difficulty=True
        ),
        "expect_level": "emergency"
    },
    {
        "name": "Major bleeding (emergency)",
        "intake": IntakeAnswers(
            name="Test Patient",
            location_query="Karachi Pakistan",
            symptoms=["bleeding", "dizziness"],
            major_bleeding=True,
            chest_pain=False
        ),
        "expect_level": "emergency"
    },
    {
        "name": "Head trauma/injury (high)",
        "intake": IntakeAnswers(
            name="Test Patient",
            location_query="Karachi Pakistan",
            symptoms=["headache", "confusion", "nausea"],
            injury_trauma=True,
            unconscious=False,
            chest_pain=False
        ),
        "expect_level": "high"
    },
    {
        "name": "Mild fever (low)",
        "intake": IntakeAnswers(
            name="Test Patient",
            location_query="Karachi Pakistan",
            symptoms=["fever", "mild cough"],
            chest_pain=False,
            breathing_difficulty=False,
            injury_trauma=False
        ),
        "expect_level": "low"
    },
]

def evaluate_rule_based() -> Dict[str, Any]:
    """Run rule-based triage tests. Returns summary dict."""
    results = []
    passed = 0
    total = len(TESTS)
    
    rprint("\n[bold cyan]=== EVALUATION: Rule-Based Triage Tests ===[/bold cyan]\n")
    
    for t in TESTS:
        triage = TriageAgent().run(t["intake"])
        ok = (triage.level == t["expect_level"])
        result = {
            "test": t["name"],
            "got": triage.level,
            "expected": t["expect_level"],
            "pass": ok,
            "reason": triage.reason[:100] + "..." if len(triage.reason) > 100 else triage.reason
        }
        results.append(result)
        status = "[green]✓ PASS[/green]" if ok else "[red]✗ FAIL[/red]"
        rprint(f"{status} {t['name']}: got={triage.level}, expected={t['expect_level']}")
        passed += int(ok)
    
    summary = {
        "passed": passed,
        "total": total,
        "pass_rate": f"{passed}/{total}",
        "all_passed": (passed == total)
    }
    
    rprint(f"\n[bold]Summary: {passed}/{total} tests passed[/bold]")
    if passed == total:
        rprint("[green]✓ All tests passed![/green]")
    else:
        rprint(f"[yellow]⚠ {total - passed} test(s) failed[/yellow]")
    
    return {"results": results, "summary": summary}

# Run evaluation
eval_results = evaluate_rule_based()


# TODO (Optional): Uncomment to install and use faster-whisper for audio transcription.
# !pip -q install faster-whisper

# from faster_whisper import WhisperModel
# def transcribe_audio(path: str) -> str:
#     model = WhisperModel("small", device="cpu", compute_type="int8")
#     segments, info = model.transcribe(path)
#     text = "".join(seg.text for seg in segments)
#     return text

# # Example:
# # print(transcribe_audio("/kaggle/input/YOUR_AUDIO_FILE.wav"))
