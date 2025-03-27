from mitmproxy import io
import gzip
import io as iio
import json
from collections import defaultdict
from datetime import datetime

def parse_record(record):
    """Parse a single record into type and key-value pairs."""
    parts = record.split(';')
    record_type = parts[0]
    data = {}
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            data[key] = value
    return record_type, data

def convert_to_decimal_odds(fractional_odds):
    """Convert fractional odds (e.g., '1/2') to decimal format."""
    if not fractional_odds or '/' not in fractional_odds:
        return None
    try:
        num, denom = map(int, fractional_odds.split('/'))
        return round((num / denom) + 1, 3)
    except (ValueError, ZeroDivisionError):
        return None

def parse_date(bc_value):
    """Parse bet365's date format."""
    try:
        return datetime.strptime(bc_value, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return bc_value

def parse_bet365_data(data_string):
    """Parse bet365's market data with focus on player props and odds."""
    records = data_string.split('|')
    matches = []
    current_match = None
    current_category = None

    players = {}  # short_id -> player data
    full_to_short_id = {}  # PCxxx -> xxx
    current_match_id = None

    for record in records:
        if not record:
            continue
        record_type, data = parse_record(record)

        if record_type == 'MG' and 'NA' in data and 'DAL Mavericks @ ORL Magic' in data['NA']:
            current_match = {
                'id': data.get('ID'),
                'name': data['NA'],
                'start_time': None,
                'league': None,
                'players': []
            }
            matches.append(current_match)

        elif record_type == 'MG' and 'BC' in data and current_match:
            current_match['start_time'] = parse_date(data['BC'])
            current_match['league'] = data.get('L3')

        elif record_type == 'CO':
            current_category = data.get('NA')  # e.g. '1', '2', etc.

        elif record_type == 'PA':
            pa_id = data.get('ID')
            if pa_id.startswith('PC'):
                short_id = pa_id[2:]
                full_to_short_id[pa_id] = short_id
                players[short_id] = {
                    'id': short_id,
                    'name': data.get('NA'),
                    'team': data.get('N2'),
                    'jersey_number': data.get('NC'),
                    'odds': {}
                }
            elif 'OD' in data:
                player_id = data.get('ID')
                if player_id in players and current_category:
                    players[player_id]['odds'][current_category] = {
                        'fractional': data['OD'],
                        'decimal': convert_to_decimal_odds(data['OD'])
                    }

    if current_match:
        for pid, player in players.items():
            current_match['players'].append(player)

    return matches

def process_bet365_traffic():
    """Process bet365 market data from captured mitmproxy traffic"""
    with open("response.txt", "r", encoding="utf-8") as f:
        raw_data = f.read()

    print("Processing raw response data...")
    try:
        matches = parse_bet365_data(raw_data)

        print("\nParsed Matches:")
        for match in matches:
            print(f"\nMatch: {match['name']}")
            print(f"League: {match['league']}")
            print(f"Start Time: {match['start_time']}")
            print("\nPlayers and Odds:")
            for player in match['players']:
                print(f"\n  {player['name']} ({player['team']}) - #{player['jersey_number']}")
                for threshold, odds in sorted(player['odds'].items(), key=lambda x: int(x[0])):
                    print(f"    Threshold {threshold}: {odds['decimal']} (decimal) / {odds['fractional']} (fractional)")
    except Exception as e:
        print(f"Error processing response: {str(e)}")

if __name__ == "__main__":
    process_bet365_traffic()
