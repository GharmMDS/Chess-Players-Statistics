import json
import os
import re
import sys
import logging
import pandas as pd
from sqlalchemy import create_engine

from sqlalchemy import text

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- File Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # Directory of openingdatabase.py
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR)) # Go up two levels to the project root
DATA_DIR = os.path.join(PROJECT_ROOT, 'data') # The 'data' directory at the root level (this might not be used now)
OPENING_NAMES_FILE_PATH = os.path.join(PROJECT_ROOT, 'opening_names.csv') # Saving at the root level for simplicity

# Ensure the root directory exists for the output CSV
os.makedirs(PROJECT_ROOT, exist_ok=True)

# --- Database Connection Details ---
DB_URL = "postgresql://postgres:gharm@localhost:5432/chess_data"
DB_TABLE_NAME = "games"
DB_COLUMN_NAME = "eco"

def extract_eco_from_pgn(pgn):
    eco_match = re.search(r'\[ECO\s+"(.*?)"\]', pgn)
    if eco_match:
        return eco_match.group(1)
    return "unknown"

def process_json_files(player):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir)) # Go up two levels to the project root
    player_json_dir = os.path.join(project_root, player)
    extracted_openings = []

    if not os.path.exists(player_json_dir):
        logging.error(f"JSON data directory not found: {player_json_dir}")
        return pd.DataFrame()

    for filename in os.listdir(player_json_dir):
        if filename.endswith(".json") and filename.startswith(f"{player}_games_"):
            filepath = os.path.join(player_json_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    games = json.load(f)
                    for game in games:
                        pgn = game.get("pgn", "")
                        eco_code = extract_eco_from_pgn(pgn)
                        game_id = game.get("uuid", game.get("url", "").split('/')[-1])
                        extracted_openings.append({
                            "player": player,
                            "game_id": game_id,
                            "eco_code": eco_code
                        })
            except IOError as e:
                logging.error(f"Error reading JSON file {filepath}: {e}")
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON in {filepath}: {e}")

    openings_df = pd.DataFrame(extracted_openings)
    return openings_df

def save_opening_data_to_csv(df):
    if not df.empty:
        if os.path.exists(OPENING_NAMES_FILE_PATH):
            try:
                existing_df = pd.read_csv(OPENING_NAMES_FILE_PATH)
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                combined_df = combined_df.drop_duplicates(subset=["player", "game_id"], keep="first")
                combined_df.to_csv(OPENING_NAMES_FILE_PATH, index=False)
                logging.info(f"Appended {len(df)} entries. Total entries: {len(combined_df)}")
            except Exception as e:
                logging.error(f"Error reading or writing to CSV: {e}")
        else:
            df.to_csv(OPENING_NAMES_FILE_PATH, index=False)
            logging.info(f"Created new file and saved {len(df)} entries.")
    else:
        logging.warning("No opening data extracted from JSON files.")

def update_eco_in_database(df):
    if df.empty:
        logging.warning("No opening data to update in the database.")
        return

    engine = create_engine(DB_URL)
    try:
        with engine.connect() as connection:
            for index, row in df.iterrows():
                eco_code = row['eco_code']
                game_id = row['game_id']
                sql = text(f"""
                    UPDATE {DB_TABLE_NAME}
                    SET {DB_COLUMN_NAME} = :eco
                    WHERE game_id = :game_id;
                """)
                connection.execute(sql, {"eco": eco_code, "game_id": game_id})
            connection.commit() # Ensure changes are committed to the database
            logging.info(f"Successfully updated ECO codes for {len(df)} games in the database.")
    except Exception as e:
        logging.error(f"Error updating database: {e}")
    finally:
        if engine:
            engine.dispose() # Dispose of the engine to release resources
def main():
    print(f"Script location: {os.path.abspath(__file__)}") # Keep this for debugging
    if len(sys.argv) > 1:
        player = sys.argv[1].strip().lower()
        print(f"Processing opening data for player: {player} (from command line)")
    else:
        player = input("Enter the Chess.com username to process openings for: ").strip().lower()
        print(f"Processing opening data for player: {player} (entered in terminal)")

    openings_df = process_json_files(player)
    save_opening_data_to_csv(openings_df)
    update_eco_in_database(openings_df)

if __name__ == "__main__":
    main()