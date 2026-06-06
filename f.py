import json
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def hunt_for_source():
    # 1. Load your existing JSON
    try:
        with open('perfect_tree.json', 'r', encoding='utf-8') as f:
            games = json.load(f)
    except FileNotFoundError:
        print("Could not find perfect_tree.json! Make sure it's in the same folder.")
        return

    print("Loaded JSON. Mapping directory links...")
    
    # 2. Get the links from the main page so we know exactly where to click
    base_url = "https://archive.thedatadungeon.com/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    main_page = requests.get(base_url, headers=headers)
    main_soup = BeautifulSoup(main_page.text, 'html.parser')
    
    # Build a dictionary of { "Game Name": "Link" }
    link_map = {}
    for a in main_soup.find_all('a'):
        link_map[a.text.strip()] = a.get('href')

    print(f"Mapped links. Scanning {len(games)} games for source code...\n")

    # 3. Loop through your JSON and check each game's page
    for game in games:
        name = game.get('name')
        game['source_code_status'] = "None" # Default state
        
        if name in link_map:
            # Build the full URL to the game's sub-folder
            game_url = urljoin(base_url, link_map[name])
            
            try:
                game_page = requests.get(game_url, headers=headers)
                game_soup = BeautifulSoup(game_page.text, 'html.parser')
                
                # You mentioned class="item", but standard archives often just use <a> tags or <tr>. 
                # We will grab both to be safe.
                items = game_soup.find_all(class_='item')
                if not items: 
                    items = game_soup.find_all('a')

                status = "None"
                for item in items:
                    text = item.get_text(strip=True).lower()
                    
                    # We clean the text of dots and underscores so "game_src.zip" reads as "game src zip"
                    # This prevents false hits on words that just happen to contain s-r-c.
                    clean_words = text.replace('.', ' ').replace('_', ' ').replace('-', ' ').split()
                    
                    # Check for Definite Hits
                    if 'source code' in text or 'src' in clean_words:
                        status = "Hit"
                        break # Found it! Stop searching this page.
                        
                    # Check for Guesses
                    elif 'source' in clean_words or 'sources' in clean_words:
                        status = "Guess"
                        
                game['source_code_status'] = status
                print(f"[{status.ljust(5)}] {name}")
                
            except Exception as e:
                print(f"[Error] {name}: {e}")
                
            # Be polite to The Data Dungeon's servers (clicks once every 0.2 seconds)
            time.sleep(0.2)
        else:
            print(f"[Skip ] {name} (Could not map link)")

    # 4. Save it to a NEW file so we don't ruin your original JSON if something goes wrong
    with open('perfect_tree_with_source.json', 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=4)
        
    print("\nDONE! Saved everything safely to perfect_tree_with_source.json")

if __name__ == "__main__":
    hunt_for_source()