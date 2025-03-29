import requests
from pydantic import BaseModel
from typing import Optional, List
import json
import sys
import os
from cron.models import PlayerPayload, TeamPayload

# Add the parent directory to the Python path so we can import from cron/
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# Dictionary to store team IDs
team_cache = {}
next_team_id = 1

def get_or_create_team_id(team_name: str, team_info: dict = None) -> int:
    """Get an existing team ID or create a new one"""
    global next_team_id
    
    if team_name in team_cache:
        return team_cache[team_name]
    
    # Create new team ID
    team_id = next_team_id
    team_cache[team_name] = team_id
    next_team_id += 1
    
    return team_id

# ---------------------------
# Function to Fetch NBA Players from balldontlie API
# ---------------------------
def fetch_nba_players() -> List[PlayerPayload]:
    """
    Uses the free balldontlie API to fetch all NBA players.
    This API provides paginated results.
    """
    players: List[PlayerPayload] = []
    page = 1
    per_page = 100  # Maximum items per page available on the API.
    
    while True:
        url = f"https://www.balldontlie.io/api/v1/players?page={page}&per_page={per_page}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching NBA players on page {page}")
            break
        
        data = response.json()
        for player in data.get("data", []):
            # Combine first and last names for a full name.
            full_name = f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
            team_info = player.get("team", {})
            team_name = team_info.get("full_name", "Unknown Team")
            
            # Get or create team ID
            team_id = get_or_create_team_id(team_name, team_info)
            
            # The API may not provide a position for all players.
            position = player.get("position") or None

            # Package additional details into a JSON string.
            details = json.dumps({
                "player_id": player.get("id"),
                "team_abbreviation": team_info.get("abbreviation"),
                "city": team_info.get("city"),
                "conference": team_info.get("conference"),
                "division": team_info.get("division")
            })

            players.append(PlayerPayload(
                name=full_name,
                team_id=team_id,
                position=position,
                details=details
            ))
        
        # Check pagination info.
        meta = data.get("meta", {})
        if page >= meta.get("total_pages", 0):
            break
        page += 1
    
    print(f"Fetched {len(players)} NBA players")
    return players

# ---------------------------
# Function to Fetch G-League Players from TheSportsDB API
# ---------------------------
def fetch_gleague_players() -> List[PlayerPayload]:
    """
    Uses TheSportsDB API to fetch player data for each G-League team.
    The endpoint used is 'searchplayers.php' which requires a team name.
    The free API key '1' is used (as provided by TheSportsDB for testing).
    """
    players: List[PlayerPayload] = []
    
    # Representative list of NBA G-League team names.
    gleague_team_names = [
        "Austin Spurs",
        "Long Island Nets",
        "Raptors 905",
        "Grand Rapids Drive",
        "Lakeland Magic",
        "Salt Lake City Stars",
        "South Bay Lakers",
        "Maine Red Claws",
        "Fort Wayne Mad Ants",
        "Capitanes de Ciudad de México",
        "Westchester Knicks",
        "Wisconsin Herd",
        "College Park Skyhawks",
        "Delaware Blue Coats",
        "Sioux Falls Skyforce"
    ]
    
    base_url = "https://www.thesportsdb.com/api/v1/json/1/searchplayers.php"
    for team in gleague_team_names:
        params = {"t": team}
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Error fetching G-League players for team {team}")
            continue
        
        data = response.json()
        # The key "player" holds the list of players for the team.
        if data and data.get("player"):
            for player in data["player"]:
                full_name = player.get("strPlayer")
                # Get or create team ID
                team_id = get_or_create_team_id(team)
                # Position information might be available.
                position = player.get("strPosition") or None
                # Package additional details into a JSON string.
                details = json.dumps({
                    "id": player.get("idPlayer"),
                    "dateBorn": player.get("dateBorn"),
                    "nationality": player.get("strNationality"),
                    "description": player.get("strDescriptionEN")
                })
                players.append(PlayerPayload(
                    name=full_name,
                    team_id=team_id,
                    position=position,
                    details=details
                ))
    
    print(f"Fetched {len(players)} G-League players")
    return players

# ---------------------------
# Main Function: Combine and Write JSON Output
# ---------------------------
def main():
    nba_players = fetch_nba_players()
    gleague_players = fetch_gleague_players()
    
    all_players = nba_players + gleague_players
    
    # First save teams
    teams_output = [
        TeamPayload(
            id=team_id,
            name=team_name,
            abbreviation=None,  # We can add this later if needed
            city=None,
            conference=None,
            division=None
        ).dict()
        for team_name, team_id in team_cache.items()
    ]
    
    with open("teams_seed.json", "w") as f:
        json.dump(teams_output, f, indent=2)
    print(f"Generated teams seed file with {len(teams_output)} teams")
    
    # Then save players
    all_players_dict = [player.dict() for player in all_players]
    with open("players_seed.json", "w") as f:
        json.dump(all_players_dict, f, indent=2)
    print(f"Generated players seed file with {len(all_players_dict)} players")

if __name__ == "__main__":
    main()
