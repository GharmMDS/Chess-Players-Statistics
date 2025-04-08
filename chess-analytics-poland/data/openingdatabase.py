import requests
import pandas as pd
import logging
import os
import re
import psycopg2
import csv
from sqlalchemy import create_engine

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- File Paths ---
DATA_DIR = './data'
OPENING_NAMES_FILE_PATH = os.path.join(DATA_DIR, 'opening_names.csv')
OPENINGS_SHEET_FILE_PATH = os.path.join(DATA_DIR, 'openings_sheet.csv')

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# --- Requests Session Setup ---
session = requests.Session()
session.headers.update({'User-Agent': 'QueenIsBeautiful (your_email@example.com)'})

# --- Database Connection Details ---
DB_URL = "postgresql://postgres:gharm@localhost:5432/chess_data"
DB_TABLE_NAME = "games"
DB_COLUMN_NAME = "eco"
CSV_DB_COLUMN_NAME = "eco_code" # Column in CSV to map to DB 'eco'
CSV_DB_GAME_ID_COLUMN = "game_id" # Column in CSV for game identifier

# --- Functions for Fetching and Saving Data ---
def fetch_all_game_urls(player):
    url = f"https://api.chess.com/pub/player/{player}/games/archives"
    try:
        response = session.get(url)
        response.raise_for_status()
        archives = response.json().get("archives", [])
        logging.info(f"Found {len(archives)} archives for {player}")
        return archives
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching archives: {e}")
        return []

def fetch_games_data(archive_url):
    try:
        response = session.get(archive_url)
        response.raise_for_status()
        return response.json().get("games", [])
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching games from {archive_url}: {e}")
        return []

def extract_eco_from_pgn(pgn):
    eco_match = re.search(r'\[ECO\s+"(.*?)"\]', pgn)
    if eco_match:
        return eco_match.group(1)
    return "unknown"

def save_initial_opening_data(player):
    archives = fetch_all_game_urls(player)
    if not archives:
        logging.warning("No archives found.")
        return

    extracted = []
    for archive_url in archives:
        games = fetch_games_data(archive_url)
        for game in games:
            pgn = game.get("pgn", "")
            eco = extract_eco_from_pgn(pgn)
            game_id = game.get("uuid", game["url"].split("/")[-1])
            extracted.append({
                "player": player,
                "game_id": game_id,
                "eco_code": eco
            })

    if not extracted:
        logging.warning("No games with ECO codes were extracted.")
        return

    df = pd.DataFrame(extracted)

    # Save to CSV
    if os.path.exists(OPENING_NAMES_FILE_PATH):
        try:
            existing_df = pd.read_csv(OPENING_NAMES_FILE_PATH)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df = combined_df.drop_duplicates(subset=["player", "game_id"], keep="first")
            combined_df.to_csv(OPENING_NAMES_FILE_PATH, index=False)
            logging.info(f"Appended {len(df)} entries for {player}. Total entries: {len(combined_df)}")
        except Exception as e:
            logging.error(f"Error reading or writing to CSV: {e}")
    else:
        df.to_csv(OPENING_NAMES_FILE_PATH, index=False)
        logging.info(f"Created new file and saved {len(df)} entries for {player}")

# --- Function to Update Database from CSV ---
def update_eco_from_csv_sqlalchemy():
    conn = None
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as connection:
            raw_connection = connection.connection
            cur = raw_connection.cursor()

            with open(OPENING_NAMES_FILE_PATH, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                if CSV_DB_COLUMN_NAME not in reader.fieldnames:
                    print(f"Error: Column '{CSV_DB_COLUMN_NAME}' not found in the CSV file.")
                    return
                if CSV_DB_GAME_ID_COLUMN not in reader.fieldnames:
                    print(f"Error: Column '{CSV_DB_GAME_ID_COLUMN}' not found in the CSV file.")
                    return

                for row in reader:
                    eco_code = row.get(CSV_DB_COLUMN_NAME)
                    game_id = row.get(CSV_DB_GAME_ID_COLUMN)
                    if eco_code and game_id:
                        sql = f"""
                            UPDATE {DB_TABLE_NAME}
                            SET {DB_COLUMN_NAME} = %s
                            WHERE game_id = %s;
                        """
                        cur.execute(sql, (eco_code, game_id))
                        raw_connection.commit()
                        print(f"Updated '{DB_COLUMN_NAME}' for game_id: {game_id} with '{eco_code}'")
                    else:
                        print(f"Warning: Missing '{CSV_DB_COLUMN_NAME}' or '{CSV_DB_GAME_ID_COLUMN}' in CSV row: {row}")

            print("Successfully processed the CSV file and updated the database.")

    except psycopg2.Error as e:
        print(f"Error connecting to or updating the database: {e}")
        if raw_connection:
            raw_connection.rollback()
    except FileNotFoundError:
        print(f"Error: CSV file not found at '{OPENING_NAMES_FILE_PATH}'")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if raw_connection:
            cur.close()


def main():
    player = input("Enter the Chess.com username: ").strip().lower()
    save_initial_opening_data(player)
    update_eco_from_csv_sqlalchemy()

if __name__ == "__main__":
    main()