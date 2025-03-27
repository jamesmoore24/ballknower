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

def parse_bet365_data(data_string):
    records = data_string.split('|')

    """ #Example odds = {
        'stat' : 'Threes',
        'players' : [
            {
                'player_name' : 'Player 2',
                'odds' : [{
                    'value' : '3',
                    'odds' : '1/2',
                    'type' : 'over'
                },
                {
                    'value' : '4',
                    'odds' : '1/2',
                    'type' : 'over'
                }]
            },
            {
                'player_name' : 'Player 3',
                'odds' : [{
                    'value' : '3',
                    'odds' : '1/2',
                    'type' : 'over'
                },
                {
                    'value' : '4',
                    'odds' : '1/2',
                    'type' : 'over'
                }]
            }
        ]
    }

 """
    # If a record has a 'LS=1' in it then that is a selected category like 'Threes'
    # We want to return a list of matches with the selected category
    options = []
    for record in records:
        if 'LS=1' in record:
            # MA;NA=More;PD=#AC#B18#C20604387#D43#E181378#F43#;IT=CC-MG-AF#AC#B18#C20604387#D43#E181378#F43#;LS=1;
            # Get the name of the match
            option = record.split(';')[1].split('=')[1]
            options.append(option)


    # So the response is a list of matches
    # We identify the start of a match with a record that start with 'MG'
    # After this we get a record with 'MA' that we can skip
    # Thej players are listed in order, and the odds are listed in order of the players
        # Each player has a record that starts with 'PA' 
        #PA;ID=PC411423913;NA=Johnny Juzang;N2=UTA Jazz;TD=29;IM=UTA-johnny-juzang_v1.png;NC=33;KC=#262626,#7C45CA,#262626,#7C45CA,#C40010,#0046A8,#3D4A4E,#FFFFFF,#FFFF00,#FF00FF,#F0F0F0;KI=1;TC=#262626;K1=Basket_Back_UTAJazz_City_v1.svg;PD=#AC#B18#C20604387#D48#K^12#T^29#P6948#;
        # Each record has [PA, ID (e.g. PC411423913), NA (e.g. Johnny Juzang), TD:]
        # We want to map the ID to the player name for building the odds dictionary
    # Odds start with an record that start with 'CO' (stands for column) which contains an 'NA' record which corresponds to the value of the stat of interest
        # CO;ID=C181449;NA=2;SY=ipg;PY=_d;
    # Then the following records are the odds for each player with the corresponding ID
        # The odds follow the format PA;ID=411340637;FI=171969260;OD=27/10;
            # Sometimes the OD will be OD= (empty) which means the player does not have odds for this stat at that value
        # The ID is the same as the player ID
        # The OD is the odds
    
    # Each player has a record that starts with 'PA' 
        #PA;ID=PC411423913;NA=Johnny Juzang;N2=UTA Jazz;TD=29;IM=UTA-johnny-juzang_v1.png;NC=33;KC=#262626,#7C45CA,#262626,#7C45CA,#C40010,#0046A8,#3D4A4E,#FFFFFF,#FFFF00,#FF00FF,#F0F0F0;KI=1;TC=#262626;K1=Basket_Back_UTAJazz_City_v1.svg;PD=#AC#B18#C20604387#D48#K^12#T^29#P6948#;
        # Each record has [PA, ID (e.g. PC411423913), NA (e.g. Johnny Juzang), TD:]
    selected_stat = None
    stat_categories = []
    player_map = {}
    stat_blocks = []

    # Step 1: Identify stat categories (LS=1) and get the stat name
    for record in records:
        if 'LS=1' in record and record.startswith('MA;'):
            parts = record.split(';')
            for part in parts:
                if part.startswith('NA='):
                    selected_stat = part.split('=')[1]
                    break

    # Step 2: Build player ID → name map
    for record in records:
        if record.startswith('PA;') and 'PC' in record:
            parts = record.split(';')
            pid = name = None
            for part in parts:
                if part.startswith('ID='):
                    pid = part.split('=')[1][2:]
                elif part.startswith('NA='):
                    name = part.split('=')[1]
            if pid and name:
                player_map[pid] = name

    # Step 3: Traverse odds columns
    odds = {
        'stat': selected_stat,
        'players': []
    }

    i = 0
    while i < len(records):
        record = records[i]
        if record.startswith('CO;') and selected_stat:
            # Get the value associated with this block
            value = None
            for part in record.split(';'):
                if part.startswith('NA='):
                    value = part.split('=')[1]
                    break
            
            i += 1
            # Parse entries while they start with 'CO' or 'PA' (same match)
            # Stop when we hit 'MG' (next match)
            print(f"i before: {i}")
            while i < len(records) and not records[i].startswith('MG'):
                entry = records[i]
                
                # Handle CO records - update value
                if entry.startswith('CO;'):
                    for part in entry.split(';'):
                        if part.startswith('NA='):
                            value = part.split('=')[1]
                            print(value)
                            break
                    print("HERE")
                
                # Handle PA records - parse odds
                elif entry.startswith('PA;') and 'OD=' in entry:
                    parts = entry.split(';')
                    pid = odds_val = None
                    for part in parts:
                        if part.startswith('ID='):
                            pid = part.split('=')[1]
                        elif part.startswith('OD='):
                            odds_val = part.split('=')[1]
                        elif part.startswith('FI='):    
                            fi = part.split('=')[1]
                    print(f"pid: {pid}, odds_val: {odds_val}, fi: {fi}")
                    # Look for player name in player_map
                    # Them index into the odds array and update the odds

                    if pid in player_map:
                        pname = player_map[pid]
                        print(pname)
                        # Find or create player entry
                        player_entry = next((p for p in odds['players'] if p['player_name'] == pname), None)
                        if not player_entry:
                            player_entry = {'player_name': pname, 'odds': []}
                            odds['players'].append(player_entry)
                        if odds_val:
                            player_entry['odds'].append({
                                'value': value,
                                'odds': odds_val,
                                'type': 'over'  # assumed, you may want to dynamically extract this
                            })
                i += 1
            print(f"i after: {i}")
        else:
            i += 1
    print(player_map)
    return odds


def process_bet365_traffic():
    with open("response.txt", "r", encoding="utf-8") as f:
        raw_data = f.read()

    return parse_bet365_data(raw_data)['players'][0]

if __name__ == "__main__":
    print(process_bet365_traffic())

