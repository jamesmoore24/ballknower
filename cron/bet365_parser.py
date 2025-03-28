from mitmproxy import io
from collections import defaultdict
from datetime import datetime

def parse_record(record):
    parts = record.split(';')
    record_type = parts[0]
    data = {}
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            data[key] = value
    return record_type, data

def convert_to_decimal_odds(fractional_odds):
    if not fractional_odds or '/' not in fractional_odds:
        return None
    try:
        num, denom = map(int, fractional_odds.split('/'))
        return round((num / denom) + 1, 3)
    except (ValueError, ZeroDivisionError):
        return None

def parse_date(bc_value):
    try:
        return datetime.strptime(bc_value, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return bc_value

def parse_standard_stats(records, odds, current_players, player_map, i):
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

def parse_over_under_stats(records, odds, current_players, i):
    """
    Parses Bet365-formatted records to extract Points Over/Under stats for players,
    using player names directly from 'PA;' records.

    Format:
    - 'MG;' starts a new match (reset players).
    - One or more 'PA;' lines with 'NA=' define the player names in order.
    - Followed by:
        - 'MA;' tag indicating 'Over' market.
        - N 'PA;' lines with odds values for each player.
        - 'MA;' tag indicating 'Under' market.
        - N 'PA;' lines with odds values for each player.
    - This pattern repeats per match.

    Parameters:
    - records: list of record strings
    - odds: dictionary to accumulate parsed data
    - current_players: list of player names in order
    - i: current index in records

    Returns:
    - Updated odds dictionary
    """
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
            i += 1
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

            while i < len(records):
                entry = records[i]

                if entry.startswith('MG;') or entry.startswith('MA;'):
                    break  # Next section

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


def parse_bet365_data(data_string):
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
        return parse_standard_stats(records, odds, current_players, player_map, i)
    else:
        return parse_over_under_stats(records, odds, current_players, i)

def process_bet365_traffic(mitm_file):
    all_odds = []  # List to store odds dictionaries from each API call
    
    with open(mitm_file, "rb") as f:
        flow_reader = io.FlowReader(f)
        for flow in flow_reader.stream():
            if "https://www.bet365.com.au/matchmarketscontentapi/markets" in flow.request.url:
                print(f"\nProcessing URL: {flow.request.url}")
                # Get response content and decode it
                response_content = flow.response.content.decode('utf-8')
                # Parse the response and add to all_odds list
                odds_data = parse_bet365_data(response_content)
                print(odds_data['stat'])
                print(odds_data['players'])
                if odds_data['stat'] in ['Points O/U', 'Points Low']:
                    with open('bet365_points_out.txt', 'a') as f:
                        f.write(response_content)
                if odds_data and odds_data['stat']:  # Only add if we have valid data
                    all_odds.append(odds_data)
    return all_odds

if __name__ == "__main__":
    all_odds = process_bet365_traffic("traffic.mitm")

