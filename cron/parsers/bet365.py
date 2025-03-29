from typing import Dict, Any, List
from datetime import datetime
from .base import BaseParser, parser_factory

def convert_to_decimal_odds(fractional_odds: str) -> float:
    """Convert fractional odds to decimal format"""
    if not fractional_odds or '/' not in fractional_odds:
        return None
    try:
        num, denom = map(int, fractional_odds.split('/'))
        return round((num / denom) + 1, 3)
    except (ValueError, ZeroDivisionError):
        return None

def parse_date(bc_value: str) -> str:
    """Parse date from Bet365 format to standard format"""
    try:
        return datetime.strptime(bc_value, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return bc_value

class Bet365Parser(BaseParser):
    """Parser for Bet365 traffic data"""
    
    BET365_URL = "https://www.bet365.com.au/matchmarketscontentapi/markets"
    
    def can_handle_url(self, url: str) -> bool:
        return self.BET365_URL in url

    def _parse_standard_stats(self, records: List[str], odds: Dict, current_players: List[str], 
                            player_map: Dict[str, str], i: int) -> Dict:
        """Handle parsing for Threes Made, Points, Assists, Rebounds"""
        while i < len(records):
            record = records[i]
            
            # New match starts
            if record.startswith('MG;'):
                current_players = []  # Reset players for new match
                i += 1
                continue

            # Player record
            if record.startswith('PA;') and 'PC' in record:
                parts = record.split(';')
                pid = name = None
                for part in parts:
                    if part.startswith('ID='):
                        pid = part.split('=')[1][2:]  # Remove 'PC' prefix
                    elif part.startswith('NA='):
                        name = part.split('=')[1]
                if pid and name:
                    player_map[pid] = name
                    current_players.append(pid)  # Add to ordered list
                i += 1
                continue
                
            # Stats column with odds
            if record.startswith('CO;'):
                value = None
                for part in record.split(';'):
                    if part.startswith('NA='):
                        value = part.split('=')[1]
                        break
                
                # Process odds for each player in order
                i += 1
                player_index = 0
                while i < len(records) and not records[i].startswith('MG') and not records[i].startswith('CO;'):
                    entry = records[i]
                    if entry.startswith('PA;') and 'OD=' in entry:
                        parts = entry.split(';')
                        odds_val = None
                        for part in parts:
                            if part.startswith('OD='):
                                odds_val = part.split('=')[1]
                                break
                        
                        if player_index < len(current_players):
                            pid = current_players[player_index]
                            if pid in player_map:
                                pname = player_map[pid]
                                player_entry = next((p for p in odds['players'] if p['player_name'] == pname), None)
                                if not player_entry:
                                    player_entry = {'player_name': pname, 'odds': []}
                                    odds['players'].append(player_entry)
                                if odds_val and value:
                                    player_entry['odds'].append({
                                        'value': value,
                                        'odds': odds_val,
                                        'type': 'over'
                                    })
                        player_index += 1
                    i += 1
            else:
                i += 1
        return odds

    def _parse_over_under_stats(self, records: List[str], odds: Dict, current_players: List[str], i: int) -> Dict:
        """Parse Over/Under stats for players"""
        while i < len(records) and not records[i].startswith('PA;'):
            record = records[i]
            if 'LS=1' in record and record.split(';')[1].split('=')[1] != 'More':
                odds['stat'] = record.split(';')[1].split('=')[1]
            i += 1

        while i < len(records):
            record = records[i]

            # New match
            if record.startswith('MG;'):
                current_players.clear()
                i += 2  # Skip next 'MA' record
                continue

            # Initial player list with names
            elif record.startswith('PA;') and 'NA=' in record:
                parts = record.split(';')
                name = None
                for part in parts:
                    if part.startswith('NA='):
                        name = part.split('=')[1]
                if name:
                    current_players.append(name)
                i += 1
                continue

            # Over/Under market
            elif record.startswith('MA;'):
                is_over = 'Over' in record
                i += 1
                player_index = 0

                while i < len(records) and not (records[i].startswith('MG;') or records[i].startswith('MA;')):
                    entry = records[i]

                    if entry.startswith('PA;') and 'OD=' in entry and 'HA=' in entry:
                        parts = entry.split(';')
                        odds_val = value = None
                        for part in parts:
                            if part.startswith('OD='):
                                odds_val = part.split('=')[1]
                            elif part.startswith('HA='):
                                value = part.split('=')[1]

                        if player_index < len(current_players):
                            pname = current_players[player_index]
                            player_entry = next((p for p in odds['players'] if p['player_name'] == pname), None)
                            if not player_entry:
                                player_entry = {'player_name': pname, 'odds': []}
                                odds['players'].append(player_entry)
                            if value and odds_val:
                                player_entry['odds'].append({
                                    'value': value,
                                    'odds': odds_val,
                                    'type': 'over' if is_over else 'under'
                                })
                        player_index += 1
                    i += 1
            else:
                i += 1

        return odds

    def _parse_bet365_data(self, data_string: str) -> Dict:
        """Parse Bet365 data string into structured format"""
        records = data_string.split('|')
        
        odds = {
            'stat': None,
            'players': []
        }
        
        current_players = []  # Track players in order for current match
        player_map = {}  # Keep the global player map for reference
        i = 0

        # Get stat name
        for record in records:
            if 'LS=1' in record and record.split(';')[1].split('=')[1] != 'More':
                odds['stat'] = record.split(';')[1].split('=')[1]
                break

        if odds['stat'] in ['Threes Made', 'Points', 'Assists', 'Rebounds']:
            return self._parse_standard_stats(records, odds, current_players, player_map, i)
        else:
            return self._parse_over_under_stats(records, odds, current_players, i)
        
    def process_traffic(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Bet365 traffic data and return processed results"""
        try:
            # Extract response content
            response_content = traffic_data.get('response', {}).get('content', '')
            if not response_content:
                raise ValueError("No response content found in traffic data")
                
            # Parse the response data
            odds_data = self._parse_bet365_data(response_content)
            
            # Add metadata
            processed_data = {
                'source': 'bet365',
                'url': traffic_data.get('request', {}).get('url', ''),
                'timestamp': traffic_data.get('timestamp', ''),
                'stat_type': odds_data.get('stat'),
                'players': odds_data.get('players', [])
            }
            
            return processed_data
            
        except Exception as e:
            raise Exception(f"Error processing Bet365 traffic: {str(e)}")

# Register the Bet365 parser with the factory
parser_factory.register_parser(Bet365Parser()) 