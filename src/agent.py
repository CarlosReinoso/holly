"""The Shard Receptionist - A voice AI receptionist for The Shard, London."""

import logging

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

from tools.directory import lookup_employee, search_employees_for_lookup
from tools.facility import get_available_facilities, get_facility_info
from tools.weather import lookup_weather

logger = logging.getLogger("agent")

load_dotenv(".env.local")

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
- Look up employees in the building directory
- Check employee availability
- Retrieve building information

Use tools when you need information you don't already have.

Do NOT mention tools or internal systems to the visitor. Just give the answer naturally.

Always keep your responses short, natural, and conversational since this is a voice interaction.
"""


class ShardReceptionist(Agent):
    """Voice receptionist agent for The Shard."""

    def __init__(self) -> None:
        super().__init__(instructions=RECEPTIONIST_INSTRUCTIONS)

    @function_tool
    async def search_employees_for_lookup(self, context: RunContext, query: str) -> str:
        """Search employees by name and/or department for semantic lookup.

        Use when the visitor gives a partial name or context (e.g. "John", "John from Engineering",
        "Sarah in Finance"). Returns full names and departments. Pick the correct person, then
        call lookup_employee with their full name.

        Args:
            query: Partial name and/or department (e.g. "John Engineering", "Sarah")
        """
        logger.info("Search employees: %s", query)
        return search_employees_for_lookup(query)

    @function_tool
    async def lookup_employee(self, context: RunContext, name: str) -> str:
        """Look up an employee in The Shard directory by full name.

        Call this after search_employees_for_lookup when you've resolved the correct person.
        Returns floor, department, and availability. Use the full name (e.g. "John Smith").

        Args:
            name: Full name of the person (e.g. "John Smith", "Sarah Thompson")
        """
        logger.info("Looking up employee: %s", name)
        return lookup_employee(name)

    @function_tool
    async def get_available_facilities(self, context: RunContext) -> str:
        """List available facility keys with search terms for semantic matching.

        Use when the visitor asks about a facility (e.g. "where's the loo", "parking").
        Match their wording to a facility key from this list, then call get_facility_info
        with that key.
        """
        logger.info("Listing available facilities")
        return get_available_facilities()

    @function_tool
    async def get_facility_info(self, context: RunContext, facility_key: str) -> str:
        """Get directions and information for a facility by its key.

        Call get_available_facilities first to find the correct key (e.g. "loo" -> "bathroom"),
        then pass that key here.

        Args:
            facility_key: Canonical facility key (e.g. "bathroom", "lifts", "parking", "viewing_gallery")
        """
        logger.info("Facility lookup: %s", facility_key)
        return get_facility_info(facility_key)

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
        return lookup_weather(location)


server = AgentServer()


def prewarm(proc: JobProcess) -> None:
    """Preload VAD model for faster first response."""
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="holly")
async def my_agent(ctx: JobContext) -> None:
    ctx.log_context_fields = {"room": ctx.room.name}

    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3", language="multi"),
        llm=inference.LLM(model="openai/gpt-4.1-mini"),
        tts=inference.TTS(
            model="cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"
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
    cli.run_app(server)
