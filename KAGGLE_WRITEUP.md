# EmergencyCareNavigator — AI Multi-Agent Emergency Routing & Pre‑Arrival Handoff

**Subtitle:** Faster decisions in emergencies: intake → triage flag → nearest facility + ETA → clinician handoff packet

## Problem

In emergencies, critical time is lost because people are anxious and don't know:
- what questions matter most,
- where to go (ER vs clinic),
- which facility is nearest and has the right capabilities,
- what information to share upon arrival.

This delay can worsen outcomes, especially in time-sensitive conditions like stroke, heart attack, or severe trauma.

## Solution

EmergencyCareNavigator is a multi-agent assistant that:
1. **Collects minimal emergency intake quickly** (supports voice in future app)
2. **Flags urgency conservatively** using rule-based triage (safety-first)
3. **Finds nearby hospitals/clinics** using geocoding + routing tools (Nominatim/OSRM)
4. **Generates an SBAR-style handoff packet** ready for clinicians
5. **Simulates booking** as a long-running operation requiring human approval (demonstrates pause/resume)

## Why Agents?

Multi-agent decomposition improves reliability and maintainability:
- **IntakeAgent** keeps questions short and focused
- **TriageAgent** is safety-focused and deterministic (rule-based, with optional LLM explanation)
- **FacilityFinderAgent** uses tools for real-time lookup and ranking
- **CoordinatorAgent** orchestrates the workflow and creates the handoff summary

This separation allows each agent to be tested independently and makes the system easier to extend.

## Architecture

```
IntakeAgent → TriageAgent → FacilityFinderAgent → CoordinatorAgent
                ↓                ↓                      ↓
            Rule-based      Tools (Geocode,        Handoff Packet
            + Optional      Facility Search,        + Booking State
            LLM             ETA Routing)
```

### Key Components

**Agents:**
- **IntakeAgent**: Collects emergency questionnaire (name, location, symptoms, red flags)
- **TriageAgent**: Rule-based triage with 4 levels (emergency/high/medium/low)
- **FacilityFinderAgent**: Finds and ranks nearby facilities by ETA/distance
- **CoordinatorAgent**: Orchestrates workflow, generates SBAR handoff packet

**Tools:**
- **Geocode Tool**: Nominatim API converts location text → lat/lon
- **Facility Search Tool**: Nominatim bounded search finds hospitals/clinics
- **ETA Routing Tool**: OSRM API estimates travel time
- **Booking Tool**: Simulated long-running operation (pending_approval → confirmed)

**Memory & State:**
- **Session State**: `CoordinatorAgent` maintains booking state per session
- **Long-term Memory**: `MemoryBank` (JSON) stores preferred_city and last_facility_used

**Observability:**
- Structured logging with trace_id, timestamps, event types
- Metrics counters (tool_calls, llm_calls, errors)
- All tool calls and agent actions are logged

## Capstone Concepts Demonstrated

This project demonstrates **all 5 key concepts**:

1. ✅ **Multi-Agent System**: 4 specialized agents (Intake, Triage, FacilityFinder, Coordinator)
2. ✅ **Tools**: External APIs (Nominatim, OSRM) + custom booking tool with pause/resume
3. ✅ **Sessions & Memory**: Session state (booking) + long-term memory (JSON file)
4. ✅ **Observability**: Structured logs, trace IDs, metrics counters
5. ✅ **Evaluation**: 6 rule-based test scenarios (chest pain, stroke, anaphylaxis, bleeding, trauma, mild fever)

## Value / Impact

- **Reduces decision-making time** during emergencies
- **Standardizes information** given to clinicians (SBAR format)
- **Helps caregivers stay calm** via clear, step-by-step guidance
- **Improves handoff quality** with pre-arrival summary

## Responsible AI & Limitations

**Safety First:**
- ⚠️ **No diagnosis**. This tool provides information support only.
- Always recommends emergency escalation for red flags (chest pain, stroke signs, breathing difficulty, etc.).
- Every emergency/high output includes explicit "call emergency services now" warning.

**Technical Limitations:**
- Public APIs (Nominatim/OSRM) have rate limits and may be incomplete.
- "Booking" is simulated; real integration needs official hospital/EMR APIs.
- Geocoding may fail for obscure locations (graceful error handling included).

**Data Privacy:**
- Avoids collecting unnecessary identifiers.
- Memory bank stores minimal data (preferred city, last facility).

## How to Run

1. Open the notebook in Kaggle
2. (Optional) Add `GEMINI_API_KEY` secret for LLM-powered explanations
3. Run all cells top-to-bottom
4. Use the **Demo** section (Cell 20) for interactive testing
5. Run **Evaluation** (Cell 23) to see test results

The notebook works in two modes:
- **Mock Mode** (no API key): Uses deterministic fallback for LLM explanations
- **Gemini Mode** (with API key): Generates empathetic explanations via Gemini

## Evaluation Results

The system includes 6 automated test scenarios:
- ✅ Severe chest pain → emergency
- ✅ Stroke signs → emergency
- ✅ Anaphylaxis → emergency
- ✅ Major bleeding → emergency
- ✅ Head trauma → high
- ✅ Mild fever → low

All tests pass deterministically (no external API calls in tests).

## Future Work

- Real voice agent UI (Web Speech API integration)
- Verified facility capability database (trauma center, cardiology, etc.)
- Live availability feeds from hospitals
- Offline mode & SMS fallback for low-connectivity areas
- Integration with official hospital booking systems

## Technical Details

**Dependencies:**
- `requests`: HTTP calls to Nominatim/OSRM
- `pydantic`: Structured data models
- `rich`: Enhanced terminal output
- `google-generativeai`: Optional LLM explanations (Gemini)

**Error Handling:**
- Retry logic with exponential backoff for HTTP calls
- Graceful fallback: distance-only ranking if OSRM fails
- User-friendly error messages for geocoding failures

**Code Quality:**
- Type hints throughout
- Structured error handling
- Comprehensive logging
- Deterministic tests

---

**Note**: This is a capstone project demonstrating multi-agent systems. It is not a medical device and should not be used for actual medical decision-making. Always call emergency services for true emergencies.

