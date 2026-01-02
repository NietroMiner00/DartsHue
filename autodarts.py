import requests
import json
import time
import threading
import websocket

class AutodartsClient:
    """
    A Python wrapper for the Autodarts REST API.
    """
    def __init__(self, email, password, client_id, client_secret):
        # Configuration
        self.email = email
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        
        # Base URLs
        self.AUTH_URL = "https://login.autodarts.io/realms/autodarts/protocol/openid-connect/token"
        self.BASE_URL_GS = "https://api.autodarts.io/gs/v0"
        self.BASE_URL_AS = "https://api.autodarts.io/as/v0"
        self.BASE_URL_BS = "https://api.autodarts.io/bs/v0"
        self.WS_URL = "wss://api.autodarts.io/ms/v0/subscribe"

        # Token Management
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = 0
        self.ws = None

    # --- Authentication Logic ---

    def login(self):
        """Authenticates with Keycloak and retrieves Bearer tokens."""
        payload = {
            'grant_type': 'password',
            'username': self.email,
            'password': self.password,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'openid'
        }
        response = requests.post(self.AUTH_URL, data=payload)
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data['access_token']
        self.refresh_token = data.get('refresh_token')
        self.token_expiry = time.time() + data['expires_in']
        return data

    def load_tokens(self, tokens):
        """Loads authentication tokens into the client."""
        self.access_token = tokens.get('access_token')
        self.refresh_token = tokens.get('refresh_token')
        self.token_expiry = tokens.get('token_expiry', 0)

    def refresh_access_token(self):
        """Refreshes the access token using the refresh token."""
        if not self.refresh_token:
            return self.login()

        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.post(self.AUTH_URL, data=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data.get('refresh_token', self.refresh_token) # Keep old one if not provided
            self.token_expiry = time.time() + data['expires_in']
            return data
        else:
            # If refresh fails, fall back to a full login
            return self.login()
 
    def _get_headers(self):
        """Ensures token is valid and returns authorization headers."""
        if time.time() >= self.token_expiry:
            self.refresh_access_token()
        return {'Authorization': f'Bearer {self.access_token}'}

    # --- API Actions ---

    def get_matches(self):
        """Fetches all active matches."""
        res = requests.get(f"{self.BASE_URL_GS}/matches/", headers=self._get_headers())
        return res.json()

    def get_match_state(self, match_id):
        """Fetches state for a specific match."""
        res = requests.get(f"{self.BASE_URL_GS}/matches/{match_id}", headers=self._get_headers())
        return res.json()

    def next_player(self, match_id):
        """Signals the next player to throw."""
        res = requests.post(f"{self.BASE_URL_GS}/matches/{match_id}/players/next", headers=self._get_headers())
        return res.status_code == 204

    def undo_throw(self, match_id):
        """Undoes the last registered throw."""
        res = requests.post(f"{self.BASE_URL_GS}/matches/{match_id}/undo", headers=self._get_headers())
        return res.status_code == 204

    def next_game(self, match_id):
        """Moves match to the next game/leg."""
        res = requests.post(f"{self.BASE_URL_GS}/matches/{match_id}/games/next", headers=self._get_headers())
        return res.status_code == 204

    def start_match_from_lobby(self, lobby_id):
        """Starts a match from an existing lobby."""
        res = requests.post(f"{self.BASE_URL_GS}/lobbies/{lobby_id}/start", headers=self._get_headers())
        return res.json()

    def get_user_stats(self, user_id, variant='x01', limit=10):
        """Retrieves statistics for a specific user."""
        url = f"{self.BASE_URL_AS}/users/{user_id}/stats/{variant}?limit={limit}"
        res = requests.get(url, headers=self._get_headers())
        return res.json()
    
    def get_boards(self):
        """Retrieves the local IP address for a specific board."""
        res = requests.get(f"{self.BASE_URL_BS}/boards/", headers=self._get_headers())
        return res.json()

    def get_board_ip(self, board_id):
        """Retrieves the local IP address for a specific board."""
        res = requests.get(f"{self.BASE_URL_BS}/boards/{board_id}", headers=self._get_headers())
        return res.json().get('ip')
    
    # --- WebSocket Logic ---

    def subscribe(self, channel, topic):
        """Subscribes to a specific channel (e.g., 'autodarts.matches') and topic (match ID)."""
        if self.ws and self.ws.sock and self.ws.sock.connected:
            params = {
                "type": "subscribe",
                "channel": channel,
                "topic": topic
            }
            self.ws.send(json.dumps(params))
            print(f"Subscribed to {channel} -> {topic}")

    def start_websocket(self, on_message_callback):
        """Starts the WebSocket in a separate background thread."""
        def run():
            self.ws = websocket.WebSocketApp(
                self.WS_URL,
                header=self._get_headers(),
                on_message=lambda ws, msg: on_message_callback(json.loads(msg)),
                on_error=lambda ws, err: print(f"WS Error: {err}"),
                on_close=lambda ws, close_code, close_msg: print("WS Closed"),
                on_open=lambda ws: print("WS Connection Opened")
            )
            self.ws.run_forever()

        wst = threading.Thread(target=run)
        wst.daemon = True
        wst.start()
        # Give the connection a moment to open
        time.sleep(2)

class Channels:
    """Available WebSocket Channels"""
    MATCHES = "autodarts.matches"
    BOARDS = "autodarts.boards"
    LOBBIES = "autodarts.lobbies"
    USERS = "autodarts.users"

    @staticmethod
    def match_state(match_id):
        """Topic for full match state updates"""
        return f"{match_id}.state"

    @staticmethod
    def board_matches(board_id):
        """Topic for match start/stop events on a specific board"""
        return f"{board_id}.matches"

    @staticmethod
    def board_events(board_id):
        """Topic for physical board events (Takeout, Calibration)"""
        return f"{board_id}.events"

    @staticmethod
    def user_events(user_id):
        """Topic for personal user notifications and lobby invites"""
        return f"{user_id}.events"
    
class BoardEvents:
    """Standard event strings sent by the board topic"""
    TAKEOUT_STARTED = "Takeout started"
    TAKEOUT_FINISHED = "Takeout finished"
    CALIBRATION_STARTED = "Calibration started"
    CALIBRATION_FINISHED = "Calibration finished"
    BOARD_STOPPED = "Stopped"
    BOARD_STARTED = "Started"
    MANUAL_RESET = "Manual reset"