# update_bets.py
import sqlite3
import random
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv()

# Get the database path from an environment variable, with a fallback for local dev
DB_PATH = os.environ.get('BALLKNOWER_DB_PATH')

def scrape_sample_odds():
    url = "https://example.com"  # Replace with a real sports betting site
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        odds = soup.find('span', class_='odds')
        if odds:
            return float(odds.text)
        else:
            print("No odds found on page")
            return random.uniform(1.0, 3.0)
    except requests.RequestException as e:
        print(f"Web scraping failed: {e}")
        return random.uniform(1.0, 3.0)

if __name__ == "__main__":
    scraped_odds = scrape_sample_odds()
    print(f"Scraped odds: {scraped_odds}")
    print(f"Current time: {datetime.now()}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE bets SET odds = ? WHERE team = ?", (scraped_odds, '1'))
    conn.commit()
    conn.close()
    print("Updated odds for Team A with scraped data")