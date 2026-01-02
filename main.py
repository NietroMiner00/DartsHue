import json
import os
import time
from autodarts import AutodartsClient

TOKEN_FILE = 'autodarts_tokens.json'

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading tokens: {e}")
    return None

def save_tokens(tokens):
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=4)
        print(f"Tokens saved to {TOKEN_FILE}")
    except Exception as e:
        print(f"Error saving tokens: {e}")

# Usage Example
if __name__ == "__main__":
    # In a real app, load these from config
    
    client = AutodartsClient(
        email="yourmail",
        password="yourpassword",
        client_id="yourclientid",
        client_secret="yourclientsecret"
    )

    # Try to load existing tokens
    saved_tokens = load_tokens()
    if saved_tokens:
        client.load_tokens(saved_tokens)

    try:
        # Check if we need to login (no token or expired)
        if client.access_token is None or time.time() >= client.token_expiry:
            print("Logging in...")
            new_tokens = client.login()
            save_tokens(new_tokens)
            print("Successfully logged in.")
        else:
            print("Using loaded tokens.")

        # 1. Get active matches
        matches = client.get_match_state("019b7f2c-3b22-79ca-bdba-612e51e57146")
        if matches:
            print(f"Tracking Match: {matches}")
        else:
            print("No running matches!")

    except Exception as e:
        print(f"API Error: {e}")