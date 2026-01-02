This documentation is based on the integration logic found in the **Darts-Caller** source code. It outlines the REST API and WebSocket interfaces provided by Autodarts for match management, board control, and real-time updates.

---

## 1. Authentication

Autodarts uses **Keycloak** for authentication. All requests must include a Bearer token in the header.

* **Auth URL:** `https://login.autodarts.io/`
* **Realm:** `autodarts`
* **Header:** `Authorization: Bearer <access_token>`

---

## 2. Base URLs

| Service | URL |
| --- | --- |
| **Game Service (GS)** | `https://api.autodarts.io/gs/v0/` |
| **Board Service (BS)** | `https://api.autodarts.io/bs/v0/` |
| **Account Service (AS)** | `https://api.autodarts.io/as/v0/` |
| **WebSocket Service (MS)** | `wss://api.autodarts.io/ms/v0/subscribe` |

---

## 3. REST API Endpoints

### Match Management

#### **Get Active Matches**

`GET /gs/v0/matches/`
Returns a list of currently active matches.

#### **Get Match Details**

`GET /gs/v0/matches/{match_id}`
Returns the full state of a specific match (players, scores, variant settings).

#### **Next Throw / Player Change**

`POST /gs/v0/matches/{match_id}/players/next`
Proceeds to the next player's turn.

#### **Undo Throw**

`POST /gs/v0/matches/{match_id}/undo`
Reverts the last registered throw.

#### **Next Game/Leg**

`POST /gs/v0/matches/{match_id}/games/next`
Proceeds to the next leg or set in the match.

#### **Manual Dart Correction**

`PATCH /gs/v0/matches/{match_id}/throws`
Corrects specific dart values.

* **Payload Example:**
```json
{
  "changes": {
    "0": {"point": {"x": 0.123, "y": 0.456}, "type": "normal"}
  }
}

```



### Lobby Management

#### **Start Match from Lobby**

`POST /gs/v0/lobbies/{lobby_id}/start`
Transitions a lobby into an active match.

### Board Control (Local/Remote)

These endpoints interact with the **Autodarts Board Manager** (typically a local IP).

#### **Start/Stop Detection**

`PUT /api/detection/start`
`PUT /api/detection/stop`

#### **Reset/Calibrate Board**

`POST /api/reset`
`POST /api/config/calibration/auto`

### User Statistics

#### **Get Player Average**

`GET /as/v0/users/{user_id}/stats/{variant}?limit={limit}`
Fetches scoring statistics for a specific player and game mode (e.g., `x01`).

---

## 4. WebSocket API (Real-time Events)

The WebSocket uses a pub/sub model. After connecting to `wss://api.autodarts.io/ms/v0/subscribe`, you must send a subscription message.

### Subscription Payload

```json
{
  "channel": "autodarts.matches",
  "type": "subscribe",
  "topic": "{match_id}.state"
}

```

### Available Channels

| Channel | Topic | Purpose |
| --- | --- | --- |
| `autodarts.boards` | `{board_id}.matches` | Notifications for match starts/stops on a board. |
| `autodarts.boards` | `{board_id}.events` | Physical board events (Takeout started, Calibration). |
| `autodarts.matches` | `{match_id}.state` | Full match state updates (darts thrown, scores). |
| `autodarts.lobbies` | `{lobby_id}.state` | Lobby updates (players joining/leaving). |
| `autodarts.users` | `{user_id}.events` | Personal notifications (lobby invites). |

---

## 5. Match State Data Structure

When receiving data from the `autodarts.matches` channel, the payload usually contains:

* **`variant`**: The game mode (`X01`, `Cricket`, `ATC`, `CountUp`, `Bermuda`, `Shanghai`, `Gotcha`).
* **`player`**: Index of the current player.
* **`turns`**: Array of the current turn's throws.
* **`gameScores`**: Current points remaining/accumulated.
* **`winner` / `gameWinner**`: Set to player index upon match/leg completion; otherwise `-1`.

---

## 6. Supported Game Variants

The API handles different logic based on the `variant` field:

* **X01**: Typical countdown logic with `baseScore`.
* **Cricket**: Tracking hits on segments 15-20 and Bull.
* **Bermuda**: Round-based targets where missing halves the score.
* **Gotcha**: Scoring to reach a target exactly, resetting opponents if scores match.

Would you like me to generate a specific Python or JavaScript client example for one of these endpoints?