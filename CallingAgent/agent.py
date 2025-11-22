import asyncio
import json
import logging
import os
from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.voice import Agent
from livekit.plugins import openai, silero

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Configure logging
logger = logging.getLogger("calling-agent")
logger.setLevel(logging.INFO)

# Load context
CONTEXT_FILE = "call_context.json"
OUTCOME_FILE = "call_outcome.json"

def load_context():
    try:
        with open(os.path.join(os.path.dirname(__file__), CONTEXT_FILE), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"{CONTEXT_FILE} not found. Using default context.")
        return {
            "shop_name": "Plumbing Shop",
            "item_name": "Plumbing Item",
            "pickup_time": "sometime today"
        }

CALL_CONTEXT = load_context()

@llm.function_tool(description="Save the details of the reservation availability and price.")
def save_reservation_details(
    available: bool,
    price: float,
    confirmed_time: str,
    notes: str,
):
    """
    Called when the user (shop owner) confirms availability, price, and pickup time.

    Args:
        available: Whether the item is available in stock.
        price: The price of the item per unit.
        confirmed_time: The confirmed pickup time.
        notes: Any additional notes (e.g., reservation name, contact person).
    """
    logger.info(f"Saving reservation details: Available={available}, Price={price}, Time={confirmed_time}")

    outcome_data = {
        "item_available": available,
        "price": price,
        "reserved_pickup_time": confirmed_time,
        "notes": notes
    }

    try:
        output_path = os.path.join(os.path.dirname(__file__), OUTCOME_FILE)
        with open(output_path, "w") as f:
            json.dump(outcome_data, f, indent=2)
        logger.info(f"Successfully saved outcome to {output_path}")
        return "Details saved successfully. You can now end the call."
    except Exception as e:
        logger.error(f"Failed to save outcome: {e}")
        return "Failed to save details."

async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext()

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    agent = Agent(
        vad=silero.VAD.load(),
        stt=openai.STT(),
        llm=openai.LLM(model="gpt-4o"),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        fnc_ctx=llm.FunctionContext(),
        instructions=(
            f"You are a professional plumber's assistant calling {CALL_CONTEXT.get('shop_name', 'a shop')} on behalf of a plumber. "
            f"Your goal is to find out if they have {CALL_CONTEXT.get('item_name')} in stock. "
            f"If they have it, ask for the price and try to reserve it for pickup around {CALL_CONTEXT.get('pickup_time')}. "
            "Be polite but direct. "
            "If the price is provided, record it. "
            "Once you have the information (availability, price, confirmed time) and have made a reservation (if possible), "
            "call the `save_reservation_details` tool to save the information, and then politely say goodbye and end the conversation."
        ),
    )

    agent.fnc_ctx.register(save_reservation_details)

    agent.start(ctx.room, participant)

    logger.info("Agent started, waiting for 1 second before greeting...")
    await asyncio.sleep(1)
    logger.info("Attempting to say greeting...")
    await agent.say("Hello, I'm calling to check stock for a plumbing item. Do you have a moment?", allow_interruptions=True)
    logger.info("Greeting sent.")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
