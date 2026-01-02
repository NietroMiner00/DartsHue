import json
import os
import time
from autodarts import AutodartsClient, Channels, BoardEvents
from dotenv import load_dotenv

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
    print(data)
    event_data = data.get('data', {})
    if 'turns' in event_data:
        throws = event_data['turns'][0].get('throws', [])
        if throws:
            last_throw = throws[-1]
            print(f"🎯 Dart Thrown: {last_throw['segment']['name']} (Points: {event_data['turns'][0]['points']})")
    
    # Filter for Board Channel
    if data.get('channel') == Channels.BOARDS:
        board_status = event_data.get('event')

        if board_status == BoardEvents.TAKEOUT_STARTED:
            print("🚨 Status: Player is pulling darts. DO NOT THROW!")
        
        elif board_status == BoardEvents.TAKEOUT_FINISHED:
            print("✅ Status: Board is clear. READY TO THROW.")

        elif board_status == BoardEvents.CALIBRATION_STARTED:
            print("⚙️ Status: Board is calibrating...")

        elif board_status == BoardEvents.BOARD_STARTED:
            print("🚀 Status: Detection engine is online.")

# Usage Example
if __name__ == "__main__":
    load_dotenv()
    
    # Creds from env file
    client = AutodartsClient(
        email=os.getenv("AUTODARTS_EMAIL"),
        password=os.getenv("AUTODARTS_PASSWORD"),
        client_id=os.getenv("AUTODARTS_CLIENT_ID"),
        client_secret=os.getenv("AUTODARTS_CLIENT_SECRET")
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

        boards = client.get_boards()
        board = None
        if boards:
            board = boards[0]
            client.subscribe(Channels.BOARDS, Channels.board_events(board["id"]))

        # 2. Find a match to listen to
        matches = client.get_matches()
        if matches:
            match_id = matches[0]['id']
            # 3. Subscribe to the state of this match
            client.subscribe(Channels.MATCHES, Channels.match_state(match_id))
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