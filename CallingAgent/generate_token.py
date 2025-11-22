import os
from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants

# Load from the .env in the same directory
load_dotenv(dotenv_path=".env")

api_key = os.getenv("LIVEKIT_API_KEY")
api_secret = os.getenv("LIVEKIT_API_SECRET")
url = os.getenv("LIVEKIT_URL")

if not all([api_key, api_secret, url]):
    print("Error: Missing LIVEKIT_API_KEY, LIVEKIT_API_SECRET, or LIVEKIT_URL in .env")
    exit(1)

# Create a token for a user to join a room
grant = VideoGrants(room_join=True, room="playground-room")
token = AccessToken(api_key, api_secret).with_grants(grant).with_identity("human_user").with_name("Human User").to_jwt()

print("\n--- CONNECTION DETAILS ---")
print(f"LiveKit URL: {url}")
print(f"Token: {token}")
print("\nINSTRUCTIONS:")
print("1. Go to https://agents-playground.livekit.io/")
print("2. Ensure you are in 'Manual' mode or paste these details into the connection settings.")
print("3. URL: " + url)
print("4. Token: " + token)
print("5. Room Name (if asked): playground-room")
print("6. Click Connect.")
print("--------------------------\n")

