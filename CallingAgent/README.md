# Calling Agent

This agent calls a plumbing shop to inquire about item availability and reserves a pickup time.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You might need to use a public PyPI index if you are in a restricted environment: `pip install -r requirements.txt --index-url https://pypi.org/simple`)*

2.  **Environment Variables:**
    Ensure you have a `.env` file in this directory (`CallingAgent/.env`) with the following keys:
    - `LIVEKIT_URL`
    - `LIVEKIT_API_KEY`
    - `LIVEKIT_API_SECRET`
    - `OPENAI_API_KEY`

3.  **Context:**
    Edit `call_context.json` to change the shop name, item, and pickup time.

## Running the Agent

To run the agent in development mode (connecting to a local or cloud playground):

```bash
python agent.py dev
```

Then connect to the playground to interact with the agent.

## Output

The agent will save the result of the call (availability, price, confirmed time) to `call_outcome.json`.

