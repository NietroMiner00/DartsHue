import requests
import json
import time

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

        # Token Management
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = 0

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
 
    def _get_headers(self):
        """Ensures token is valid and returns authorization headers."""
        if time.time() >= self.token_expiry:
            self.login()
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

    def get_board_ip(self, board_id):
        """Retrieves the local IP address for a specific board."""
        res = requests.get(f"{self.BASE_URL_BS}/boards/{board_id}", headers=self._get_headers())
        return res.json().get('ip')