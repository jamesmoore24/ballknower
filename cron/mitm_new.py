from mitmproxy import io
import gzip
import io as iio
import json
from collections import defaultdict
from datetime import datetime

# Function to parse a single record (e.g., F|CL;ID=18;...)
def parse_record(record):
    parts = record.split(';')
    record_type = parts[0]  # e.g., F, EV, MG, MA, PA, CO
    data = {}
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            data[key] = value
    return record_type, data

# Function to convert odds (e.g., "1/2") to decimal odds
def convert_to_decimal_odds(fractional_odds):
    if not fractional_odds or '/' not in fractional_odds:
        return None
    try:
        num, denom = map(int, fractional_odds.split('/'))
        return round((num / denom) + 1, 2)  # Decimal odds = (numerator/denominator) + 1
    except (ValueError, ZeroDivisionError):
        return None

# Function to parse the date from the BC field (e.g., 20250327231000)
def parse_date(bc_value):
    try:
        return datetime.strptime(bc_value, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return bc_value

# Main parsing logic
def parse_bet365_data(data_string):
    records = data_string.split('|')
    matches = []
    current_match = None
    current_market = None
    current_category = None
    current_players = []

    for record in records:
        if not record:
            continue
        record_type, record_data = parse_record(record)

        if record_type == 'F':
            # Frame record (likely metadata for the entire response)
            pass  # We can store this if needed, but it doesn't seem critical for now

        elif record_type == 'EV':
            # Event record (e.g., a basketball match)
            current_match = {
                'id': record_data.get('ID'),
                'category': record_data.get('TB', '').split(',')[0] if 'TB' in record_data else None,
                'subcategory': record_data.get('TB', '').split('¬')[1] if 'TB' in record_data and '¬' in record_data.get('TB') else None,
                'markets': []
            }
            matches.append(current_match)

        elif record_type == 'MG':
            # Market group record (e.g., a specific match or market category)
            if 'NA' in record_data and 'DAL Mavericks @ ORL Magic' in record_data['NA']:
                current_match['teams'] = record_data['NA']
                current_match['start_time'] = parse_date(record_data.get('BC', ''))
                current_match['league'] = record_data.get('L3')
            current_market = {
                'id': record_data.get('ID'),
                'name': record_data.get('NA'),
                'symbol': record_data.get('SY'),
                'categories': []
            }
            if current_match:
                current_match['markets'].append(current_market)

        elif record_type == 'MA':
            # Market record (e.g., "Game", "1st Half", "Player Multi")
            market_data = {
                'id': record_data.get('ID'),
                'name': record_data.get('NA'),
                'path': record_data.get('PD'),
                'item_type': record_data.get('IT'),
                'categories': []
            }
            if current_market:
                current_market['categories'].append(market_data)
                current_category = market_data

        elif record_type == 'CO':
            # Category odds record (e.g., "1", "2", ..., "9" for different stat thresholds)
            category_data = {
                'name': record_data.get('NA'),
                'symbol': record_data.get('SY'),
                'players': []
            }
            if current_category:
                current_category['categories'].append(category_data)
                current_players = category_data['players']

        elif record_type == 'PA':
            # Player record (e.g., player stats and odds)
            player_data = {
                'id': record_data.get('ID'),
                'name': record_data.get('NA'),
                'team': record_data.get('N2'),
                'team_id': record_data.get('TD'),
                'number': record_data.get('NC'),
                'odds': record_data.get('OD'),
                'decimal_odds': convert_to_decimal_odds(record_data.get('OD')),
                'suspended': record_data.get('SU') == '1'
            }
            if current_players is not None:
                current_players.append(player_data)

    return matches

# Main script
def main():
    # Load the saved traffic
    with open("traffic.mitm", "rb") as f:
        flow_reader = io.FlowReader(f)
        for flow in flow_reader.stream():
            if "https://www.bet365.com.au/matchmarketscontentapi/markets" in flow.request.url:
                print(f"\nProcessing URL: {flow.request.url}")
                
                try:
                    # Use response text directly
                    data_string = flow.response.text

                    # Parse the data
                    matches = parse_bet365_data(data_string)

                    # Print the parsed data in a readable format
                    for match in matches:
                        print(f"\nMatch: {match.get('teams', 'Unknown Teams')}")
                        print(f"League: {match.get('league', 'Unknown League')}")
                        print(f"Start Time: {match.get('start_time', 'Unknown Time')}")
                        for market in match['markets']:
                            print(f"  Market: {market.get('name', 'Unknown Market')}")
                            for category in market['categories']:
                                print(f"    Category: {category.get('name', 'Unknown Category')}")
                                for sub_category in category['categories']:
                                    print(f"      Sub-Category: {sub_category['name']}")
                                    for player in sub_category['players']:
                                        print(f"        Player: {player['name']} ({player['team']})")
                                        print(f"          Odds: {player['odds']} (Decimal: {player['decimal_odds']})")
                                        print(f"          Suspended: {player['suspended']}")

                    # Save to a JSON file
                    with open("parsed_bet365_data.json", "w") as json_file:
                        json.dump(matches, json_file, indent=2)
                    print("\nParsed data saved to 'parsed_bet365_data.json'")

                except Exception as e:
                    print(f"Error processing response: {str(e)}")
                    print("Raw content (first 100 bytes):", flow.response.content[:100])

if __name__ == "__main__":
    main()