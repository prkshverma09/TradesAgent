<!-- 12a76bad-ece3-45dd-a16c-9dcd01a8ba5a 65c9534d-b091-4e34-905b-5719547dcfb3 -->
# Calling Agent Plan

This plan outlines the creation of a Voice Agent using the LiveKit Agents framework. The agent will act as a plumber's assistant, calling plumbing shops to negotiate purchases.

## 1. Project Structure

- Create a new directory `CallingAgent/`.
- All agent-related code and configuration will reside here.

## 2. Environment & Dependencies

- **File**: `CallingAgent/requirements.txt`
    - `livekit-agents`
    - `livekit-plugins-openai`
    - `livekit-plugins-silero` (optional, for VAD)
    - `python-dotenv`
- **File**: `CallingAgent/.env` (template)
    - `LIVEKIT_URL`
    - `LIVEKIT_API_KEY`
    - `LIVEKIT_API_SECRET`
    - `OPENAI_API_KEY`

## 3. Input & Output Data

- **Input**: The agent needs context for each call.
    - **File**: `CallingAgent/call_context.json` (Simulated input for development)
    - **Structure**:
      ```json
      {
        "shop_name": "Plumb Center",
        "item_name": "15mm Copper Pipe (3m length)",
        "pickup_time": "2:00 PM today"
      }
      ```

- **Output**: The agent must save the outcome.
    - **File**: `CallingAgent/call_outcome.json`
    - **Structure**:
      ```json
      {
        "item_available": true,
        "price": 15.50,
        "reserved_pickup_time": "2:00 PM",
        "notes": "Spoke to Steve, reserved under name 'Mike'."
      }
      ```


## 4. Agent Implementation (`CallingAgent/agent.py`)

### A. Setup & Imports

- Import `livekit.agents`, `livekit.plugins.openai`, `AutoSubscribe`, `JobContext`, `WorkerOptions`.
- Load environment variables.
- Load `call_context.json` to get `SHOP_NAME`, `ITEM_NAME`, `PICKUP_TIME`.

### B. Tool Definition

- Create a function `save_reservation_details` annotated with `@llm.ai_callable`.
- **Parameters**:
    - `available` (bool): Is the item in stock?
    - `price` (float): Price per unit (if available).
    - `confirmed_time` (str): The agreed pickup time.
    - `notes` (str): Any special instructions or reservation names.
- **Logic**: Writes these details to `CallingAgent/call_outcome.json` and potentially terminates the call/agent.

### C. System Prompt

- Construct a dynamic system prompt using the input context.
- **Persona**: "You are a professional plumber's assistant calling {SHOP_NAME}."
- **Goal**: "Find out if they have {ITEM_NAME} in stock. If yes, ask for the price and try to reserve it for pickup around {PICKUP_TIME}."
- **Behavior**: "Be polite but direct. If the price is too high (make up a threshold if needed or just record it), just record it. Once you have the info, call the `save_reservation_details` tool and then say goodbye."

### D. VoicePipelineAgent Configuration

- Initialize `VoicePipelineAgent`.
- **VAD**: Use Silero VAD or default.
- **STT**: OpenAI Whisper (`stt=openai.STT()`).
- **LLM**: OpenAI GPT-4o (`llm=openai.LLM()`).
- **TTS**: OpenAI TTS (`tts=openai.TTS()`).
- **ChatCtx**: Initialize with the System Prompt.
- **FncCtx**: Register the `save_reservation_details` tool.

### E. Entry Point

- Use `cli.run_app(WorkerOptions(entrypoint=entrypoint_fnc))` to start the agent worker.

## 5. Execution & Testing

- **Development Mode**:
    - Run `python CallingAgent/agent.py dev`
    - Connect to the local playground (or LiveKit Cloud playground) to simulate the shop owner talking to the agent.
    - Verify `call_outcome.json` is created after the conversation.

### To-dos

- [ ] Create CallingAgent directory and config files (requirements.txt, .env, call_context.json)
- [ ] Implement agent.py with VoicePipelineAgent, System Prompt, and save_reservation_details tool