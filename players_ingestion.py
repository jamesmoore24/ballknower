import requests
import json
import os
import time
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class BallDontLieAPI:
    def __init__(self, api_key: str):
        self.base_url = "https://api.balldontlie.io/v1"
        self.api_key = api_key
        self.headers = {
            "Authorization": self.api_key
        }

    def get_all_teams(self) -> List[Dict]:
        """
        Retrieve all teams from the API.
        
        Returns:
            List[Dict]: List of team dictionaries
        """
        response = requests.get(
            f"{self.base_url}/teams",
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
        
        return response.json().get("data", [])

    def get_players_by_team(self, team_id: int, per_page: int = 100) -> List[Dict]:
        """
        Retrieve all players for a specific team.
        
        Args:
            team_id (int): The ID of the team
            per_page (int): Number of results per page (max 100)
            
        Returns:
            List[Dict]: List of player dictionaries
        """
        all_players = []
        page = 1
        
        while True:
            params = {
                "per_page": per_page,
                "page": page,
                "team_ids[]": team_id
            }
            
            try:
                response = requests.get(
                    f"{self.base_url}/players",
                    headers=self.headers,
                    params=params
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    print(f"Rate limit hit, waiting 60 seconds...")
                    time.sleep(60)
                    continue
                
                if response.status_code != 200:
                    raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
                
                data = response.json()
                players = data.get("data", [])
                
                if not players:
                    break

                print(f"Found {players}")
                    
                all_players.extend(players)
                page += 1
                
                # Add a small delay between requests to be nice to the API
                time.sleep(1)
                
            except Exception as e:
                print(f"Error fetching players for team {team_id}: {str(e)}")
                break
            
        return all_players

def save_data_to_file(data: Dict, filename: str):
    """Save data to a JSON file with timestamp."""
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Saved data to {filename}")

def main():
    # Get API key from environment variable
    api_key = os.getenv("BALLDONTLIE_API_KEY")
    if not api_key:
        raise ValueError("Please set the BALLDONTLIE_API_KEY environment variable")
    
    # Initialize API client
    api = BallDontLieAPI(api_key)
    
    try:
        # First get all teams
        print("Fetching all teams...")
        teams = api.get_all_teams()
        print(f"Successfully retrieved {len(teams)} teams")
        
        # Save teams data
        save_data_to_file(teams, "teams_data.json")
        
        # Now get players for each team
        print("\nFetching players for each team...")
        all_players = []
        
        for team in teams:
            team_id = team["id"]
            team_name = team["full_name"]
            print(f"\nFetching players for {team_name} (ID: {team_id})...")
            
            team_players = api.get_players_by_team(team_id)
            all_players.extend(team_players)
            
            print(f"Found {len(team_players)} players for {team_name}")
        
        # Save all players data
        print(f"\nTotal players found: {len(all_players)}")
        save_data_to_file(all_players, "players_data.json")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main() 