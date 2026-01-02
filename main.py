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

def handle_live_data(data):
    """Callback function that prints data whenever a dart is thrown."""
    event_data = data.get('data', {})
    if 'turns' in event_data:
        throws = event_data['turns'][0].get('throws', [])
        if throws:
            last_throw = throws[-1]
            print(f"🎯 Dart Thrown: {last_throw['segment']['name']} (Points: {event_data['turns'][0]['points']})")

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
        # Check if we have a token, if not, login and save it
        if client.access_token is None:
            print("No token found, logging in...")
            new_tokens = client.login()
            save_tokens(new_tokens)
            print("Successfully logged in and tokens saved.")
        else:
            print("Loaded tokens from file.")

        # 1. Start the background listener
        client.start_websocket(on_message_callback=handle_live_data)

        # 2. Find a match to listen to
        matches = client.get_matches()
        if True:#matches:
            match_id = "019b7f5d-5a5c-787e-93ab-9cae6b62ea22"#matches[0]['id']
            # 3. Subscribe to the state of this match
            client.subscribe("autodarts.matches", f"{match_id}.state")
        else:
            print("No running matches!")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")

    except Exception as e:
        print(f"API Error: {e}")