import json
import os
import time
from autodarts import AutodartsClient, Channels, BoardEvents
from dotenv import load_dotenv
from python_hue_v2 import Hue
import requests

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

    if data.get('channel') == Channels.MATCHES:
        finished = event_data.get("gameFinished")
        if finished:
            url = f"http://{os.getenv("HUE_BRIDGE_IP")}/api/{os.getenv("HUE_USER_TOKEN")}/lights/{light_id2}/state"
        
            # Payload for White:
            # 'mirek' 153 is Cool (6500K), 500 is Warm (2000K)
            payload = {
                "on": True,
                "bri": 254,  # Max brightness (0-254)
                "xy": [0.2695, 0.6253]    # Neutral white (~4000K)
            }
            
            response = requests.put(url, json=payload)

            for i in range(20):
                payload = {
                    "on": False
                }
                
                response = requests.put(url, json=payload)

                time.sleep(0.5)

                payload = {
                    "on": True
                }
                
                response = requests.put(url, json=payload)

                time.sleep(0.5)
    
    # Filter for Board Channel
    if data.get('channel') == Channels.BOARDS:
        board_status = event_data.get('event')

        if board_status == "start":
            print("🚀 Status: Match started")
            match_id = event_data.get("id")
            client.subscribe(Channels.MATCHES, Channels.match_state(match_id))
            
            hue.lights[light_id].color_xy = {'x': 0.2695, 'y': 0.6253}
            url = f"http://{os.getenv("HUE_BRIDGE_IP")}/api/{os.getenv("HUE_USER_TOKEN")}/lights/{light_id2}/state"
    
            # Payload for White:
            # 'mirek' 153 is Cool (6500K), 500 is Warm (2000K)
            payload = {
                "on": True,
                "bri": 254,  # Max brightness (0-254)
                "ct": 250    # Neutral white (~4000K)
            }
            
            response = requests.put(url, json=payload)
        elif board_status == BoardEvents.TAKEOUT_STARTED:
            print("🚨 Status: Player is pulling darts. DO NOT THROW!")
            hue.lights[light_id].color_xy = {'x': 0.4913, 'y': 0.4587}
        
        elif board_status == BoardEvents.TAKEOUT_FINISHED:
            print("✅ Status: Board is clear. READY TO THROW.")
            hue.lights[light_id].color_xy = {'x': 0.2695, 'y': 0.6253}
            url = f"http://{os.getenv("HUE_BRIDGE_IP")}/api/{os.getenv("HUE_USER_TOKEN")}/lights/{light_id2}/state"
    
            # Payload for White:
            # 'mirek' 153 is Cool (6500K), 500 is Warm (2000K)
            payload = {
                "on": True,
                "bri": 254,  # Max brightness (0-254)
                "ct": 250    # Neutral white (~4000K)
            }
            
            response = requests.put(url, json=payload)

        elif board_status == BoardEvents.CALIBRATION_STARTED:
            print("⚙️ Status: Board is calibrating...")
            hue.lights[light_id].color_xy = {'x': 0.6904, 'y': 0.3078}

        
        elif board_status == BoardEvents.CALIBRATION_FINISHED:
            print("⚙️ Status: Calibration finished...")
            hue.lights[light_id].color_xy = {'x': 0.2695, 'y': 0.6253}
            url = f"http://{os.getenv("HUE_BRIDGE_IP")}/api/{os.getenv("HUE_USER_TOKEN")}/lights/{light_id2}/state"
    
            # Payload for White:
            # 'mirek' 153 is Cool (6500K), 500 is Warm (2000K)
            payload = {
                "on": True,
                "bri": 254,  # Max brightness (0-254)
                "ct": 250    # Neutral white (~4000K)
            }
            
            response = requests.put(url, json=payload)

        elif board_status == BoardEvents.BOARD_STARTED:
            print("🚀 Status: Detection engine is online.")
            hue.lights[light_id].color_xy = {'x': 0.2695, 'y': 0.6253}
            url = f"http://{os.getenv("HUE_BRIDGE_IP")}/api/{os.getenv("HUE_USER_TOKEN")}/lights/{light_id2}/state"
    
            # Payload for White:
            # 'mirek' 153 is Cool (6500K), 500 is Warm (2000K)
            payload = {
                "on": True,
                "bri": 254,  # Max brightness (0-254)
                "ct": 250    # Neutral white (~4000K)
            }
            
            response = requests.put(url, json=payload)
            
        elif board_status == BoardEvents.BOARD_STOPPED:
            print("🚀 Status: Detection engine is offline.")
            hue.lights[light_id].color_xy = {'x': 0.6904, 'y': 0.3078}
            url = f"http://{os.getenv("HUE_BRIDGE_IP")}/api/{os.getenv("HUE_USER_TOKEN")}/lights/{light_id2}/state"
    
            # Payload for White:
            # 'mirek' 153 is Cool (6500K), 500 is Warm (2000K)
            payload = {
                "on": True,
                "bri": 254,  # Max brightness (0-254)
                "xy": [0.6904, 0.3078]    # Neutral white (~4000K)
            }
            
            response = requests.put(url, json=payload)

        elif board_status == BoardEvents.MANUAL_RESET:
            print("🚀 Status: Manual reset.")
            hue.lights[light_id].color_xy = {'x': 0.2695, 'y': 0.6253}
            url = f"http://{os.getenv("HUE_BRIDGE_IP")}/api/{os.getenv("HUE_USER_TOKEN")}/lights/{light_id2}/state"
    
            # Payload for White:
            # 'mirek' 153 is Cool (6500K), 500 is Warm (2000K)
            payload = {
                "on": True,
                "bri": 254,  # Max brightness (0-254)
                "ct": 250    # Neutral white (~4000K)
            }
            
            response = requests.put(url, json=payload)

        elif board_status == "Throw detected":
            print("🎯 Throw detected.")
            segment = event_data.get("throw").get("segment")
            multiplier = int(segment.get("multiplier"))
            number = int(segment.get("number"))
            global darts_sum
            throwNumber = event_data.get("throwNumber")
                
            if throwNumber == 1:
                darts_sum = 0
            darts_sum += number * multiplier
            if throwNumber == 3:
                hue.lights[light_id].color_xy = {'x': 0.4913, 'y': 0.4587}
                if darts_sum == 180:
                    url = f"http://{os.getenv("HUE_BRIDGE_IP")}/api/{os.getenv("HUE_USER_TOKEN")}/lights/{light_id2}/state"
        
                    # Payload for White:
                    # 'mirek' 153 is Cool (6500K), 500 is Warm (2000K)
                    payload = {
                        "on": True,
                        "bri": 254,  # Max brightness (0-254)
                        "xy": [0.2695, 0.6253]    # Neutral white (~4000K)
                    }
                    
                    response = requests.put(url, json=payload)
                elif darts_sum >= 100:
                    url = f"http://{os.getenv("HUE_BRIDGE_IP")}/api/{os.getenv("HUE_USER_TOKEN")}/lights/{light_id2}/state"
        
                    # Payload for White:
                    # 'mirek' 153 is Cool (6500K), 500 is Warm (2000K)
                    payload = {
                        "on": True,
                        "bri": 254,  # Max brightness (0-254)
                        "xy": [0.3114, 0.1242]    # Neutral white (~4000K)
                    }
                    
                    response = requests.put(url, json=payload)
                elif darts_sum >= 60:
                    url = f"http://{os.getenv("HUE_BRIDGE_IP")}/api/{os.getenv("HUE_USER_TOKEN")}/lights/{light_id2}/state"
        
                    # Payload for White:
                    # 'mirek' 153 is Cool (6500K), 500 is Warm (2000K)
                    payload = {
                        "on": True,
                        "bri": 254,  # Max brightness (0-254)
                        "xy": [0.1532, 0.0485]    # Neutral white (~4000K)
                    }
                    
                    response = requests.put(url, json=payload)
                

# Usage Example
if __name__ == "__main__":
    load_dotenv()
    hue = Hue(os.getenv("HUE_BRIDGE_IP"), os.getenv("HUE_USER_TOKEN"))
    bridge = hue.bridge
    light_id = int(os.getenv("HUE_LIGHT_ID"))
    light_id2 = int(os.getenv("HUE_LIGHT_ID2"))
    darts_sum = 0

    hue.lights[light_id].color_xy = {'x': 0.6904, 'y': 0.3078}
    
    url = f"http://{os.getenv("HUE_BRIDGE_IP")}/api/{os.getenv("HUE_USER_TOKEN")}/lights/{light_id2}/state"
    
    # Payload for White:
    # 'mirek' 153 is Cool (6500K), 500 is Warm (2000K)
    payload = {
        "on": True,
        "bri": 254,  # Max brightness (0-254)
        "xy": [0.6904, 0.3078]#"ct": 250    # Neutral white (~4000K)
    }
    
    response = requests.put(url, json=payload)
    
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

        # Reconnection Loop if websockets disconnect
        while True:
            # 1. Start the background listener
            client.start_websocket(on_message_callback=handle_live_data)

            # Wait for websocket connection
            while not client.ws_is_connected():
                pass

            boards = client.get_boards()
            board = None
            if boards:
                board = boards[0]
                client.subscribe(Channels.BOARDS, Channels.board_events(board["id"]))
                client.subscribe(Channels.BOARDS, f"{board['id']}.matches")

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

                    if not client.ws_is_connected():
                        break
            except KeyboardInterrupt:
                print("Exiting...")
                break

    except Exception as e:
        print(f"API Error: {e}")
