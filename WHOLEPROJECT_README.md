# Prepair - Automated Parts Procurement for Tradesmen

## Overview

Prepair is an AI-powered system that automates the parts procurement process for tradesmen (plumbers, electricians, etc.), saving them valuable time by handling store calls and booking collection times automatically.

## System Architecture

The system consists of three main components:

1. **LiveKit Agent (BackOffice Agent)** - Voice interface for the tradesman
2. **FastAPI Backend** - Orchestration layer coordinating the workflow
3. **TypeScript Microservice** - ElevenLabs agent controller for shop communication

## Complete Workflow

### Step 1: Initial Call from Plumber

A plumber calls the **LiveKit BackOffice Agent**, which:
- Answers the call and starts a conversation with the tradesman
- Collects critical information:
  - What part(s) the plumber needs
  - The plumber's current location
  - Any specific requirements or preferences

### Step 2: Backend Orchestration

The LiveKit Agent uses a **LiveKit tool** to call the **FastAPI backend** at the `/procurePart` endpoint.

The FastAPI orchestration layer then:
- Receives the part requirements and location data
- Queries **Valyu** (supplier database/API) to find stores in the area that stock the required part
- Identifies the best matching stores based on:
  - Proximity to the plumber's location
  - Part availability
  - Store ratings/reliability

### Step 3: Store Communication

For each potential store, the FastAPI backend sends an HTTP request to a **separate TypeScript microservice** which:
- Triggers an **ElevenLabs AI Agent**
- The ElevenLabs Agent calls the tool shop directly
- Conducts a natural conversation with the shop staff to:

  **Goal A:** Verify part availability
  - Confirm they have the specific part in stock
  - Check quantity available
  - Verify part specifications match requirements

  **Goal B:** Book a collection time
  - Negotiate an available pickup time slot
  - Confirm reservation under the plumber's name
  - Obtain any reference numbers or confirmation details

### Step 4: Response Chain

The response flows back through the system:

1. **ElevenLabs Agent → TypeScript Microservice**: Returns conversation outcome (availability + booking details)
2. **TypeScript Microservice → FastAPI Backend**: Formatted response with:
   - Part availability status
   - Collection time (if booked)
   - Store details and contact information
   - Any special instructions
3. **FastAPI Backend → LiveKit Agent**: Aggregated results from all contacted stores
4. **LiveKit Agent → Plumber**: Delivers the final information via voice:
   - "Good news! I found your [part name] at [store name]"
   - "It's reserved for collection at [time]"
   - "The store is located at [address], about [X] minutes from your current location"

## Key Benefits

- **Time Savings**: Plumber continues working while AI handles store calls
- **Efficiency**: Multiple stores can be contacted simultaneously
- **Convenience**: Everything handled through a single phone call
- **Reliability**: Automated confirmation and booking system
- **Hands-Free**: Perfect for tradesmen actively working on-site

## Technical Stack

- **LiveKit Agent** (Python) - Voice AI and tradesman interface
- **FastAPI** (Python) - Backend orchestration and API integration
- **TypeScript Microservice** - ElevenLabs agent controller
- **ElevenLabs Agent** - Natural language phone conversation with shops
- **Valyu** - Parts supplier database/locator service
- **Fly.io** - Cloud deployment platform for the FastAPI backend

## Deployment

The **FastAPI backend is deployed on Fly.io**, making it accessible from anywhere. This cloud deployment ensures:
- **Global Accessibility**: LiveKit agents can connect to the backend from any location
- **High Availability**: Reliable uptime for tradesman calls at any time
- **Scalability**: Can handle multiple concurrent procurement requests
- **Low Latency**: Fast response times for real-time voice conversations

## Current Status

The FastAPI backend orchestration layer is currently **unfinished** and under active development. The core endpoints and workflow logic are being implemented.

## Future Enhancements

- Multi-part procurement in single call
- Price comparison across stores
- Automatic delivery scheduling
- Integration with tradesman calendar systems
- Parts recommendation based on job description
- Historical tracking and analytics
