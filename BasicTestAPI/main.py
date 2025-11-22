from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import logging
from datetime import datetime
from pathlib import Path

# Import Valyu service
try:
    from valyu_service import ValyuSearchService, StoreResult
    VALYU_AVAILABLE = True
except ImportError:
    VALYU_AVAILABLE = False
    ValyuSearchService = None
    StoreResult = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="LiveKit Agent API", version="1.0.0")

# Add CORS middleware to allow requests from LiveKit Agent
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directory if it doesn't exist
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize Valyu service (if available)
valyu_service = None
if VALYU_AVAILABLE:
    try:
        valyu_service = ValyuSearchService()
        logger.info("Valyu service initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize Valyu service: {e}")
        logger.warning("/api/findStores endpoint will return an error")

# Pydantic model for the request body
class ProcurePartRequest(BaseModel):
    part_to_acquire: str
    location_postcode: str

# Response model for findStores
class FindStoresResponse(BaseModel):
    status: str
    message: str
    total_stores: int
    stores: List[dict]
    part_to_acquire: str
    location_postcode: str

async def _procure_part_handler(request: ProcurePartRequest):
    """
    Internal handler for part procurement requests.
    """
    try:
        # Log the incoming request
        logger.info(f"Received procure part request: {request.model_dump()}")

        # Create a unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"procure_part_{timestamp}.json"
        filepath = OUTPUT_DIR / filename

        # Prepare data to save
        data = {
            "timestamp": datetime.now().isoformat(),
            "part_to_acquire": request.part_to_acquire,
            "location_postcode": request.location_postcode
        }

        # Write to JSON file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Successfully saved request to {filepath}")

        return {
            "status": "success",
            "message": "Part procurement request received and saved",
            "filename": filename,
            "data": data
        }

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/procurePart")
async def procure_part_camel(request: ProcurePartRequest):
    """
    Endpoint to receive part procurement requests from LiveKit Agent (camelCase URL).
    Saves the request data to a JSON file in the output directory.
    """
    return await _procure_part_handler(request)

@app.post("/api/procure_part")
async def procure_part_snake(request: ProcurePartRequest):
    """
    Endpoint to receive part procurement requests from LiveKit Agent (snake_case URL).
    Saves the request data to a JSON file in the output directory.
    """
    return await _procure_part_handler(request)

@app.post("/api/findStores")
@app.post("/api/find_stores")
async def find_stores(request: ProcurePartRequest):
    """
    Find stores selling a specific part near a UK postcode using Valyu API.

    This endpoint uses the Valyu search service to find plumbing/trade stores
    that sell the requested part near the specified location.

    Args:
        request: Contains part_to_acquire and location_postcode

    Returns:
        List of stores with name, URL, and content/description
    """
    try:
        # Check if Valyu service is available
        if not VALYU_AVAILABLE or valyu_service is None:
            raise HTTPException(
                status_code=503,
                detail="Valyu service is not available. Check VALYU_API_KEY is set."
            )

        # Log the incoming request
        logger.info(f"Finding stores for: {request.model_dump()}")

        # Call Valyu search service
        stores = valyu_service.search_stores(
            part_to_acquire=request.part_to_acquire,
            location_postcode=request.location_postcode,
            max_results=10
        )

        logger.info(f"Found {len(stores)} stores for {request.part_to_acquire} near {request.location_postcode}")

        return {
            "status": "success",
            "message": f"Found {len(stores)} stores",
            "total_stores": len(stores),
            "stores": stores,
            "part_to_acquire": request.part_to_acquire,
            "location_postcode": request.location_postcode
        }

    except ValueError as e:
        # Validation errors (invalid postcode, missing fields, etc.)
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except RuntimeError as e:
        # Valyu API errors
        logger.error(f"Valyu API error: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Search service error: {str(e)}")

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in findStores: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "LiveKit Agent API is running",
        "valyu_available": VALYU_AVAILABLE and valyu_service is not None
    }

@app.get("/api/procurePart/list")
async def list_requests():
    """Optional endpoint to list all saved procurement requests"""
    try:
        files = list(OUTPUT_DIR.glob("procure_part_*.json"))
        requests = []

        for file in sorted(files, reverse=True):
            with open(file, 'r') as f:
                data = json.load(f)
                requests.append({
                    "filename": file.name,
                    "data": data
                })

        return {
            "total": len(requests),
            "requests": requests
        }
    except Exception as e:
        logger.error(f"Error listing requests: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing requests: {str(e)}")
