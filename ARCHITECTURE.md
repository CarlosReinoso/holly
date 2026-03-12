# Holly — Architecture & Design

This document describes the project concept, public APIs, workflow, and architecture of Holly, the voice AI receptionist for The Shard in London.

---

## 1. Project Concept

**Holly** is a voice AI receptionist application that powers **Holly**, a virtual receptionist for [The Shard](https://www.the-shard.com/) in London. Visitors speak to Holly over voice (via web, mobile app, or telephony) to:

- **Directory lookup** — Find people in the building (floor, room, company, availability)
- **Facility directions** — Get directions to bathrooms, lifts, café, parking, viewing gallery, etc.
- **Weather** — Current weather for London and other UK cities
- **Current time** — "What time is it?" or meeting context
- **Public holidays** — "Is the office open tomorrow?" (UK bank holidays)
- **Natural conversation** — Short, human responses; no robotic scripts

Holly handles ambiguous queries (e.g. "John" when there are two Johns), disambiguation, and availability statuses like *in a meeting*, *away*, *out to lunch*.

---

## 2. Public APIs Used

The project integrates with **no API keys required** for external services:

| Service | Purpose | Base URL | Notes |
|--------|---------|----------|-------|
| **Open-Meteo** | Weather & geocoding | `https://api.open-meteo.com/v1`, `https://geocoding-api.open-meteo.com/v1/search` | Free, no key. Used for current conditions and resolving city names to coordinates. |
| **World Time API** | Current time by timezone | `https://worldtimeapi.org/api/timezone` | Free, no key. IANA timezone support (e.g. `Europe/London`). |
| **Nager.Date** | UK public holidays | `https://date.nager.at/api/v3/PublicHolidays` | Free, no key. Used for GB holidays, filtered to England. |

### LiveKit Cloud Inference (hosted services)

Holly uses LiveKit Cloud for STT, LLM, and TTS. These are invoked via the LiveKit Agents SDK and do not require direct HTTP calls from application code:

| Component | Model | Purpose |
|-----------|-------|---------|
| **STT** | Deepgram Nova 3 (multi-language) | Speech-to-text |
| **LLM** | OpenAI GPT-4.1 mini | Natural language understanding and response generation |
| **TTS** | Cartesia Sonic 3 | Text-to-speech |

### Other LiveKit components

- **Turn detection** — LiveKit Multilingual Model for natural turn-taking
- **VAD** — Silero VAD for voice activity detection (preloaded at startup)
- **Noise cancellation** — LiveKit BVC (or BVCTelephony for SIP calls)

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT / USER                                      │
│  (Web, iOS, Flutter, SIP/telephony)                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ LiveKit RTC (WebRTC / SIP)
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LIVEKIT CLOUD / SERVER                               │
│  Rooms, participants, media routing, job dispatch                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ Agent job (room connect)
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENT WORKER (agent.py)                                   │
│  AgentServer → JobContext → AgentSession                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  STT (Deepgram) → LLM (GPT-4.1 mini) + tools → TTS (Cartesia)               │
│  VAD + Turn Detection + Noise Cancellation                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         │                              │                              │
         ▼                              ▼                              ▼
┌─────────────────┐         ┌─────────────────────┐         ┌─────────────────┐
│  tools/         │         │  db/                 │         │  External APIs  │
│  directory.py   │◄───────►│  repository.py       │         │  Open-Meteo     │
│  facility.py    │         │  mock.py             │         │  World Time     │
│  weather.py     │         │  __init__.py         │         │  Nager.Date     │
│  time.py        │         └─────────────────────┘         └─────────────────┘
│  holidays.py    │
└─────────────────┘
```

---

## 4. Project Workflow

### 4.1 Startup & job handling

1. **Agent worker starts** — `uv run python src/agent.py start` (or `dev`, `console`).
2. **Prewarm** — Silero VAD is loaded into the worker process to avoid first-user latency.
3. **Agent registration** — `@server.rtc_session(agent_name="holly")` registers the agent so LiveKit can dispatch jobs.
4. **Job received** — When a user joins a room or initiates a call, LiveKit sends a job to the worker.
5. **Session creation** — `AgentSession` is created with STT, LLM, TTS, turn detection, and VAD.
6. **Room connection** — `session.start(agent=ShardReceptionist(), room=ctx.room)` attaches Holly to the room.
7. **Connect** — `ctx.connect()` connects the worker to the room and begins handling audio.

### 4.2 Per-turn conversation flow

```
User speaks
    │
    ▼
┌─────────────────────┐
│ STT (Deepgram)      │  Audio → text transcript
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ LLM (GPT-4.1 mini)  │  Interprets intent, may call tools
└─────────────────────┘
    │
    ├──► Tool call (e.g. search_persons_for_lookup)
    │         │
    │         ▼
    │    Tool executes (calls db or external API)
    │         │
    │         ▼
    │    Result returned to LLM
    │         │
    │         └──► LLM may call more tools or generate reply
    │
    ▼
┌─────────────────────┐
│ TTS (Cartesia)      │  Text → audio
└─────────────────────┘
    │
    ▼
User hears response
```

### 4.3 Tool orchestration

The LLM decides when to call tools based on conversation context. Typical flows:

- **Directory lookup:** `search_persons_for_lookup` → (if needed) disambiguation → `lookup_person`
- **Facility:** `get_available_facilities` → match visitor wording → `get_facility_info`
- **Weather / time / holidays:** Single tool call per request

All tools return **voice-friendly strings**; the agent does not expose internal structure to the visitor.

---

## 5. Component Design

### 5.1 Agent (`src/agent.py`)

- **`ShardReceptionist`** — Extends LiveKit `Agent` with system instructions (Holly’s personality and conversation guidelines) and `@function_tool` methods.
- **`AgentServer`** — Single server instance; handles job dispatch and lifecycle.
- **`prewarm`** — Loads Silero VAD into `JobProcess.userdata` for reuse across sessions.
- **`my_agent`** — RTC session handler; creates `AgentSession`, wires STT/LLM/TTS, and connects to the room.
- **Noise cancellation** — `BVCTelephony` for SIP participants, `BVC` for others.

### 5.2 Tools layer (`src/tools/`)

| Tool | Module | External API | Description |
|------|--------|--------------|-------------|
| `search_persons_for_lookup` | directory.py | db | Search by partial name/company |
| `lookup_person` | directory.py | db | Full lookup with floor, room, availability |
| `get_available_facilities` | facility.py | db | List facility keys and search terms |
| `get_facility_info` | facility.py | db | Directions for a facility key |
| `lookup_weather` | weather.py | Open-Meteo | Current weather for a location |
| `get_current_time` | time.py | World Time API | Current time by IANA timezone |
| `check_public_holiday` | holidays.py | Nager.Date | UK public holiday check |

Tools are synchronous wrappers around `db` and HTTP; the agent’s `@function_tool` methods are async and delegate to these.

### 5.3 Repository layer (`src/db/`)

- **`Repository`** — Abstract interface (`search_persons`, `search_persons_by_context`, `get_person`, `get_all_facilities`, `get_facility`).
- **`MockRepository`** — In-memory implementation with mock directory and facility data; used for dev and tests.
- **`db` module** — Facade that delegates to the active repository. For production, swap `_repo` to a DB-backed implementation (PostgreSQL, REST API, etc.) without changing tools.

### 5.4 Data flow

```
User utterance
    → STT transcript
    → LLM (with tool definitions in context)
    → [Optional] Tool call(s)
    → Tool → db or HTTP
    → Tool → voice-friendly string
    → LLM generates final reply
    → TTS
    → Audio to user
```

---

## 6. Deployment

- **Dockerfile** — Multi-stage build; installs deps, runs `download-files`, and runs `uv run src/agent.py start`.
- **Production** — Replace `MockRepository` in `src/db/__init__.py` with a real backend before deploying.
- **Environment** — `.env.local` holds `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` (or via `lk app env`).

---

## 7. Testing

- **Unit tests** — `tests/test_db.py`, `tests/test_tools.py` for db and tools.
- **Agent evals** — `tests/test_agent.py` uses LiveKit’s LLM-as-judge pattern for:
  - Friendliness on greeting
  - Grounding (refusal when unknown info)
  - Safety (refusal of harmful requests)

Run with `uv run pytest`.
