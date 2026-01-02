from autodarts import AutodartsClient

# Usage Example
if __name__ == "__main__":
    # In a real app, load these from config
    client = AutodartsClient(
        email="yourmail",
        password="yourpassword",
        client_id="yourclientid",
        client_secret="yourclientsecret"
    )

    try:
        client.login()
        print("Successfully logged in.")

        # 1. Get active matches
        matches = client.get_matches()
        if matches:
            first_match_id = matches[0]['id']
            print(f"Tracking Match: {first_match_id}")

            # 2. Trigger next player
            client.next_player(first_match_id)
            
        # 3. Get user stats
        stats = client.get_user_stats("some-user-uuid")
        print(f"Player Average: {stats.get('average', {}).get('average')}")

    except Exception as e:
        print(f"API Error: {e}")