import requests
from bs4 import BeautifulSoup
import json
import time

# --- CONFIG ---
RAWG_KEY = "981d66ce72844992bb4e77c4f999baf9"
SOURCE_URL = "https://archive.thedatadungeon.com/"

def get_rawg_data(game_name):
    """Fetches the primary console/platform from RAWG API."""
    try:
        url = f"https://api.rawg.io/api/games?key={RAWG_KEY}&search={game_name}&page_size=1"
        response = requests.get(url).json()
        
        if response.get('results'):
            game = response['results'][0]
            # Extract platform names
            platforms = [p['platform']['name'] for p in game.get('platforms', [])]
            return ", ".join(platforms) if platforms else "Unknown"
    except Exception as e:
        return f"Error: {e}"
    return "Not Found"

def run_scrape():
    print(f"Connecting to {SOURCE_URL}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        r = requests.get(SOURCE_URL, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.find_all('tr')[1:] # Skip table header
        
        total = len(rows)
        print(f"Found {total} games. Starting enrichment...\n")
        
        final_list = []

        for i, row in enumerate(rows):
            cols = row.find_all('td')
            if not cols: continue
            
            name = cols[0].get_text(strip=True)
            if not name or "Parent" in name: continue

            # Get the console from RAWG
            console = get_rawg_data(name)
            
            # Print progress to console
            print(f"[{i+1}/{total}] {name} -> {console}")

            game_obj = {
                "name": name,
                "console": console,
                "stats": {
                    "distros": cols[1].text.strip(),
                    "images": cols[2].text.strip(),
                    "videos": cols[3].text.strip()
                },
                "status": cols[4].text.strip(),
                "year": cols[5].text.strip()
            }
            final_list.append(game_obj)
            
            # RAWG allows about 100 requests per minute, so a tiny sleep keeps us safe
            time.sleep(0.1)

        # Save to JSON
        with open('perfect_tree.json', 'w', encoding='utf-8') as f:
            json.dump(final_list, f, indent=4)
            
        print(f"\nSUCCESS! {len(final_list)} games saved to perfect_tree.json")

    except Exception as e:
        print(f"Main Error: {e}")

if __name__ == "__main__":
    run_scrape()