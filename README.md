<a href="https://livekit.io/">
  <img src="./.github/assets/livekit-mark.png" alt="LiveKit logo" width="100" height="100">
</a>

# Holly — The Shard Receptionist

A voice AI receptionist for [The Shard](https://www.the-shard.com/) in London. Visitors speak to **Holly**, a friendly virtual receptionist who looks up people in the directory, gives directions to facilities, and answers common building questions—all over voice, powered by [LiveKit Agents](https://github.com/livekit/agents) and [LiveKit Cloud](https://cloud.livekit.io/).

---

## What it does

- **Directory lookup** — "I'm here to see John from Smith Engineering" → floor, room, company, and availability
- **Facility directions** — Bathrooms, lifts, waiting area, café, parking, viewing gallery, and more
- **Weather** — "What's the weather like?" (useful when visitors are about to head outside)
- **Current time** — "What time is it?" or "John's in a meeting — it's 3:10 PM, he should be free around 3:30"
- **Public holidays** — "Is the office open tomorrow?" or "Is it a bank holiday?"
- **Natural conversation** — Short, human responses; no robotic scripts

Holly handles ambiguous queries (e.g. "John" when there are two Johns), disambiguation, and availability statuses like *in a meeting*, *away*, *out to lunch*.

---

## Project structure

```
src/
├── agent.py          # LiveKit agent entrypoint, Holly’s system prompt, and tool bindings
├── db/
│   ├── repository.py # Abstract interface for directory/facility data
│   ├── mock.py       # In-memory mock (used for dev and tests)
│   └── __init__.py   # Module facade that delegates to the active repository
└── tools/
    ├── directory.py  # Person search and lookup (formatted for voice)
    ├── facility.py   # Facility catalog and info
    ├── weather.py    # Open-Meteo API integration
    ├── time.py       # World Time API (current time)
    ├── holidays.py   # Nager.Date (UK public holidays)
    └── __init__.py   # Tool exports
```

The `db` layer is abstracted so you can swap `MockRepository` for a real database or API without touching the tools. Tools return visitor-friendly strings; the agent decides when to call them based on conversation context.

---

## Dev setup

**Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/), and a [LiveKit Cloud](https://cloud.livekit.io/) account.

Clone the repo and install dependencies:

```bash
cd holly
uv sync
```

Create `.env.local` with your LiveKit credentials:

```
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
```

Or use the LiveKit CLI to populate it:

```bash
lk cloud auth
lk app env -w -d .env.local
```

---

## Run the agent

1. **Download models** (Silero VAD, turn detector) — run once before first use:

   ```bash
   uv run python src/agent.py download-files
   ```

2. **Console mode** — talk to Holly in your terminal:

   ```bash
   uv run python src/agent.py console
   ```

3. **Dev server** — for use with a frontend or telephony:

   ```bash
   uv run python src/agent.py dev
   ```

4. **Production**:

   ```bash
   uv run python src/agent.py start
   ```

---

## Frontend & telephony

| Platform | Link | Description |
|----------|------|-------------|
| **Web** | [agent-starter-react](https://github.com/livekit-examples/agent-starter-react) | React & Next.js voice UI |
| **iOS/macOS** | [agent-starter-swift](https://github.com/livekit-examples/agent-starter-swift) | Native Swift app |
| **Flutter** | [agent-starter-flutter](https://github.com/livekit-examples/agent-starter-flutter) | Cross-platform Flutter app |
| **Telephony** | [docs](https://docs.livekit.io/agents/start/telephony/) | SIP trunks for inbound/outbound calls |

---

## Tests

Unit tests cover the db layer and tools. Agent evals use LiveKit’s LLM-as-judge pattern for friendliness, grounding, and safety.

```bash
uv run pytest
```

---

## Stack

- **STT:** Deepgram Nova 3 (multi-language)
- **LLM:** OpenAI GPT-4.1 mini
- **TTS:** Cartesia Sonic 3
- **Turn detection:** LiveKit Multilingual Model
- **Noise cancellation:** LiveKit BVC (telephony variant for SIP)
- **Weather:** Open-Meteo (no API key)
- **Time:** World Time API (no key)
- **Holidays:** Nager.Date (no key)

---

## Production deployment

The repo includes a `Dockerfile`. See the [LiveKit deployment guide](https://docs.livekit.io/agents/ops/deployment/) for deploying to LiveKit Cloud or your own infrastructure.

For production, replace `MockRepository` in `src/db/__init__.py` with a real implementation (e.g. PostgreSQL, REST API) and point your tools at it.

---

## Coding assistants (Cursor, Claude Code, etc.)

This project works well with AI coding assistants. Install the [LiveKit Docs MCP server](https://docs.livekit.io/mcp) for up-to-date LiveKit documentation.

**Cursor:** [Install MCP Server](https://cursor.com/en-US/install-mcp?name=livekit-docs&config=eyJ1cmwiOiJodHRwczovL2RvY3MubGl2ZWtpdC5pby9tY3AifQ%3D%3D)

**Claude Code:**
```bash
claude mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

See [AGENTS.md](AGENTS.md) for project-specific guidance. You can adapt it to your needs.

---

## License

MIT — see [LICENSE](LICENSE).
