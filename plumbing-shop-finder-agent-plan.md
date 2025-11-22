<!-- 3abbb44c-612e-41a9-8246-4326aec02305 2b732532-0230-4590-a33d-64bd19fe8061 -->
# Plumbing Shop Finder Agent Plan

This plan outlines the steps to create a LangGraph agent that finds plumbing shops, extracts their contact details, and saves the information.

## 1. Project Setup

- [ ] Initialize a new Python project using `uv`.
- [ ] Create a `.env` file for `VALYU_API_KEY` and `FIRECRAWL_API_KEY`.
- [ ] Install dependencies: `valyu`, `firecrawl-py`, `langgraph`, `langchain-core`, `python-dotenv`.

## 2. Agent Implementation (`agent.py`)

- [ ] Define `AgentState` (TypedDict) with keys:
    - `item`: str (Input tool/material)
    - `location`: str (Input UK Postcode)
    - `shops`: list (Intermediate search results)
    - `final_results`: list (Processed data with phone numbers and addresses)

- [ ] Implement `search_shops` node:
    - Input validation: Verify `location` format approximates a UK postcode.
    - Use ValYu Python SDK to search for "plumbing shops near [UK Postcode] selling [item]".
    - Extract `title`, `url`, `content` (snippet) from results.
    - Update `shops` in state.

- [ ] Implement `extract_contact_info` node:
    - Iterate through `shops`.
    - **Strategy**:

        1. Attempt to extract **Phone Number** AND **Full UK Address** from ValYu search result `content`.
        2. If either is missing, use `FirecrawlApp` to scrape the shop's website (`url`).
        3. Use Regex/heuristics to extract phone numbers and UK addresses from the scraped text.

    - Store `name`, `phone`, `address` (full UK address), `url` in `final_results`.

- [ ] Implement `save_results` node:
    - Write `final_results` to `plumbing_shops.json`.

- [ ] Construct LangGraph:
    - Add nodes: `search`, `extract`, `save`.
    - specific flow: `START` -> `search` -> `extract` -> `save` -> `END`.
    - Compile the graph.

## 3. Execution Entry Point (`main.py`)

- [ ] Create a CLI script to accept `item` and `location` (UK Postcode) from user.
- [ ] Invoke the LangGraph agent.
- [ ] Print the path to the output JSON.

## 4. Testing

- [ ] Run with a sample query (e.g., item="copper pipe", location="SW1A 1AA").
- [ ] Verify `plumbing_shops.json` contains `address` (Full UK Address) and `phone`.

### To-dos

- [ ] Initialize project and install dependencies
- [ ] Implement AgentState and Nodes in agent.py
- [ ] Create main.py entry point