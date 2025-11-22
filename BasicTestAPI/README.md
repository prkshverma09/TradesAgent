# LiveKit Agent API - Part Procurement Test Endpoint

A simple FastAPI backend for testing LiveKit Agent tool calls.

## Features

- **POST /api/procurePart** - Receives part procurement requests and saves them to JSON files
- **POST /api/findStores** - Searches for stores selling parts using Valyu API (requires `VALYU_API_KEY`)
- Saves all procurement requests to JSON files in the `output/` directory
- Comprehensive logging for all requests and errors
- Optional GET endpoint `/api/procurePart/list` to view all saved requests

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management.

```bash
# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env and add your VALYU_API_KEY
```

## Running the Server

```bash
# Start the FastAPI server with uv
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### POST /api/procurePart

Receives part procurement requests from LiveKit Agent.

**Request Body:**
```json
{
  "part_to_acquire": "brake pads",
  "location_postcode": "SW1A 1AA"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Part procurement request received and saved",
  "filename": "procure_part_20231122_143025_123456.json",
  "data": {
    "timestamp": "2023-11-22T14:30:25.123456",
    "part_to_acquire": "brake pads",
    "location_postcode": "SW1A 1AA"
  }
}
```

### POST /api/findStores

**NEW** - Finds stores selling a specific part near a UK postcode using the Valyu API.

**Request Body:**
```json
{
  "part_to_acquire": "copper pipes",
  "location_postcode": "E1 6AN"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Found 10 stores",
  "total_stores": 10,
  "stores": [
    {
      "name": "ABC Plumbing Supplies",
      "url": "https://example.com",
      "content": "Store description and details..."
    }
  ],
  "part_to_acquire": "copper pipes",
  "location_postcode": "E1 6AN"
}
```

**Notes:**
- Requires `VALYU_API_KEY` to be set in environment
- Validates UK postcode format
- Returns up to 10 store results
- Supports both `/api/findStores` and `/api/find_stores` URLs

### GET /

Health check endpoint. Returns API status and whether Valyu service is available.

### GET /api/procurePart/list

Lists all saved procurement requests.

## Output

All requests are saved in the `output/` directory as JSON files with timestamps in the filename.

## Deployment to Fly.io

This project is configured for easy deployment to Fly.io.

### Prerequisites

1. Install the Fly.io CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Sign up/login to Fly.io:
   ```bash
   fly auth signup
   # or if you have an account:
   fly auth login
   ```

### Deploy Steps

1. **Launch the app** (first time only):
   ```bash
   fly launch --no-deploy
   ```

   This will:
   - Use the existing [fly.toml](fly.toml) configuration
   - Create the app on Fly.io
   - Ask you to confirm settings

2. **Set the Valyu API key as a secret**:
   ```bash
   fly secrets set VALYU_API_KEY=your_valyu_api_key_here
   ```

   This securely stores your API key on Fly.io without committing it to git.

3. **Deploy the application**:
   ```bash
   fly deploy
   ```

4. **Get your app URL**:
   ```bash
   fly status
   ```

   Your API will be available at: `https://basictestapi.fly.dev`

### Update Your LiveKit Tool

Once deployed, update your LiveKit Agent HTTP tool URL to:
```
https://basictestapi.fly.dev/api/procurePart
```

### Useful Fly.io Commands

```bash
# View logs
fly logs

# Check app status
fly status

# Open app in browser
fly open

# SSH into the app
fly ssh console

# Scale down to 0 machines (pause)
fly scale count 0

# Scale up to 1 machine (resume)
fly scale count 1

# Destroy the app
fly apps destroy basictestapi
```

### Cost

The configuration uses:
- **shared-cpu-1x** with **256MB RAM**
- **Auto-stop/auto-start** enabled (machines stop when idle)
- **Min machines: 0** (only runs when needed)

This should fit within Fly.io's free tier for testing!
