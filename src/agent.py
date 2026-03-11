"""The Shard Receptionist - A ) for The Shard, London.

This module defines Emma, a conversational receptionist agent that helps visitors
with directory lookups, facility directions, and general building information.
Runs on LiveKit with STT/TTS/LLM via LiveKit Cloud Inference.
"""

# Standard library
import logging

# Third-party
from dotenv import load_dotenv

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    function_tool,
    inference,
    room_io,
)
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Local application
import tools

logger = logging.getLogger("agent")

# Load environment variables from .env.local (LiveKit URL, API keys, etc.)
load_dotenv(".env.local")


# System prompt that defines Emma's role, personality, and conversation flow.
# Kept here for readability; in production you might load from a file.
RECEPTIONIST_INSTRUCTIONS = """You are Emma, a professional and friendly receptionist working at The Shard in London.

Visitors will approach your reception desk and speak to you. Your job is to assist them just like a real receptionist would in a large office building.

Your responsibilities include:
- Greeting visitors when they arrive
- Asking who they are visiting
- Looking up people in the building directory using available tools
- Directing visitors to the correct floor
- Helping with general building questions
- Handling situations where the person is unavailable
- Providing a natural, human conversation experience

Your personality:
- Warm and welcoming
- Professional and polite
- Calm and helpful
- Conversational and natural

Do NOT sound robotic or overly formal.

Conversation guidelines:

1. Always greet visitors when the interaction starts.

Example:
"Good morning! Welcome to The Shard. How can I help you today?"

2. If a visitor says they are here to meet someone, ask for the person's name if it wasn't provided.

Example:
"Of course. Who are you here to see?"

3. When a visitor gives a name, use the directory lookup tool to find the person.

If the person exists:
- Tell the visitor which floor they are on
- Direct them to the elevators

Example:
"You're here to see Daniel Clark. His office is on the 18th floor. The elevators are just behind you."

4. If the person is not found in the directory:

Politely ask for clarification.

Example:
"I'm sorry, I couldn't find that name in the building directory. Do you know which company they work for?"

5. If the person is unavailable or in a meeting:

Explain politely and offer the waiting area.

Example:
"It looks like they're currently in a meeting. You're welcome to take a seat in the lounge area and I can let them know you've arrived."

6. Answer common building questions such as:
- Where are the bathrooms?
- Where are the elevators?
- Is there a café in the building?
- Where can visitors wait?

Examples:

Bathroom:
"The restrooms are just down the hallway to your right."

Elevators:
"The elevators are directly behind the reception desk."

Waiting area:
"You're welcome to wait in the lounge area just beside the reception."

7. If the visitor arrives early for a meeting:

Example:
"You’re a bit early for the meeting. You’re welcome to wait in the lounge area and I can let them know you’ve arrived."

Tool usage rules:

You have access to tools that can:
- Look up people in the building directory (floor, room, company)
- Check person availability
- Retrieve building information (facilities, directions)
- Get the current time (useful when someone is in a meeting: "It's 3:10 PM — he should be free around 3:30")
- Check if today or tomorrow is a UK public holiday ("The office is closed tomorrow for Good Friday")
- Look up the weather

Use tools when you need information you don't already have.

Do NOT mention tools or internal systems to the visitor. Just give the answer naturally.

Always keep your responses short, natural, and conversational since this is a voice interaction.
"""


class ShardReceptionist(Agent):
    """Voice receptionist agent for The Shard.

    Extends LiveKit Agent with function tools for directory lookup, facility info,
    and weather. Tools are exposed to the LLM so Emma can answer visitor questions
    in real time.
    """

    def __init__(self) -> None:
        super().__init__(instructions=RECEPTIONIST_INSTRUCTIONS)

    async def on_enter(self) -> None:
        """Introduce Emma when the RTC session is connected."""
        await self.session.generate_reply(
            instructions=(
                "Introduce yourself as Emma, the virtual receptionist at The Shard in London. "
                "Greet the visitor warmly and offer your assistance. Keep it short and natural for voice."
            ),
        )

    @function_tool
    async def search_persons_for_lookup(self, context: RunContext, query: str) -> str:
        """Search persons by name and/or company for semantic lookup.

        Use when the visitor gives a partial name or context (e.g. "John", "John from Smith Engineering",
        "Sarah at Acme"). Returns full names and companies. Pick the correct person, then
        call lookup_person with their full name.

        Args:
            query: Partial name and/or company (e.g. "John Smith", "Sarah Acme")
        """
        logger.info("Search persons: %s", query)
        return tools.search_persons_for_lookup(query)

    @function_tool
    async def lookup_person(self, context: RunContext, name: str) -> str:
        """Look up a person in The Shard directory by full name.

        Call this after search_persons_for_lookup when you've resolved the correct person.
        Returns floor, room number, company, and availability. Use the full name (e.g. "John Smith").

        Args:
            name: Full name of the person (e.g. "John Smith", "Sarah Thompson")
        """
        logger.info("Looking up person: %s", name)
        return tools.lookup_person(name)

    @function_tool
    async def get_available_facilities(self, context: RunContext) -> str:
        """List available facility keys with search terms for semantic matching.

        Use when the visitor asks about a facility (e.g. "where's the loo", "parking").
        Match their wording to a facility key from this list, then call get_facility_info
        with that key.
        """
        logger.info("Listing available facilities")
        return tools.get_available_facilities()

    @function_tool
    async def get_facility_info(self, context: RunContext, facility_key: str) -> str:
        """Get directions and information for a facility by its key.

        Call get_available_facilities first to find the correct key (e.g. "loo" -> "bathroom"),
        then pass that key here.

        Args:
            facility_key: Canonical facility key (e.g. "bathroom", "lifts", "parking", "viewing_gallery")
        """
        logger.info("Facility lookup: %s", facility_key)
        return tools.get_facility_info(facility_key)

    @function_tool
    async def lookup_weather(
        self, context: RunContext, location: str = "London"
    ) -> str:
        """Look up current weather for a location.

        Use when the visitor asks about the weather, e.g. "What's the weather like?",
        "Should I bring a coat?", "Is it raining?". Default to London for The Shard.

        Args:
            location: City or location (default London)
        """
        logger.info("Weather lookup: %s", location)
        return tools.lookup_weather(location)

    @function_tool
    async def get_current_time(
        self, context: RunContext, timezone: str = "Europe/London"
    ) -> str:
        """Get the current time for a timezone.

        Use when the visitor asks "What time is it?" or when giving context about
        meetings, e.g. "John is in a meeting. It's 3:10 PM — he should be free around 3:30."

        Args:
            timezone: IANA timezone (default Europe/London for The Shard)
        """
        logger.info("Time lookup: %s", timezone)
        return tools.get_current_time(timezone)

    @function_tool
    async def check_public_holiday(
        self, context: RunContext, when: str = "today"
    ) -> str:
        """Check if a given day is a UK public holiday.

        Use when the visitor asks "Is the office open tomorrow?", "Was yesterday
        a bank holiday?", "What about the day after tomorrow?", or "Is 25 December
        a holiday?".

        Args:
            when: "today", "tomorrow", "yesterday", "the day before yesterday",
                "the day after tomorrow", or a specific date as YYYY-MM-DD (e.g. 2026-12-25)
        """
        logger.info("Holiday check: %s", when)
        return tools.check_public_holiday(when=when)


# Single agent server instance; used by the LiveKit worker process.
server = AgentServer()


def prewarm(proc: JobProcess) -> None:
    """Preload Silero VAD into the worker process.

    Running this at startup avoids the first-user latency hit when the VAD
    would otherwise be loaded on the first audio frame.
    """
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="holly")
async def my_agent(ctx: JobContext) -> None:
    """Handle each incoming job: create session, attach to room, connect."""
    ctx.log_context_fields = {"room": ctx.room.name}

    # STT/TTS/LLM via LiveKit Cloud Inference; turn detection and VAD for
    # natural turn-taking. BVCTelephony for SIP calls, BVC for others.
    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3", language="multi"),
        llm=inference.LLM(model="openai/gpt-4.1-mini"),
        tts=inference.TTS(
            model="cartesia/sonic-3", voice="62ae83ad-4f6a-430b-af41-a9bede9286ca"
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    await session.start(
        agent=ShardReceptionist(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)  # Handles download-files, dev, start, console, etc.
