import json
import os
import re
import sys
import datetime
import logging
import pandas as pd
from sqlalchemy import create_engine, text

# Log setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Database connection
DB_URL = "postgresql://postgres:gharm@localhost:5432/chess_data"
engine = create_engine(DB_URL)

# Function to extract the date from a PGN string
def extract_date_from_pgn(pgn):
    match = re.search(r'\[Date "(\d{4}\.\d{1,2}\.\d{1,2})"\]', pgn, re.IGNORECASE)
    if match:
        try:
            return datetime.datetime.strptime(match.group(1), '%Y.%m.%d').date().strftime('%Y-%m-%d')
        except ValueError as e:
            logging.warning(f"Invalid PGN date: {match.group(1)} — {e}")
    logging.warning("No valid Date tag found in PGN. Using default date.")
    return '1900-01-01'

# Function to process JSON files and extract dates
def process_json_files_for_dates(player):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    player_json_dir = os.path.join(project_root, player)
    extracted_dates = []

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
                        if "pgn" not in game:
                            continue
                        game_id = game.get("uuid", game.get("url", "").split('/')[-1])
                        date_time = extract_date_from_pgn(game["pgn"])
                        extracted_dates.append({"game_id": game_id, "date_time": date_time})
            except IOError as e:
                logging.error(f"Error reading JSON file {filepath}: {e}")
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON in {filepath}: {e}")

    if extracted_dates:
        df = pd.DataFrame(extracted_dates)
        return df
    else:
        logging.warning("No valid dates extracted from JSON files.")
        return pd.DataFrame()

# Function to update the database with extracted dates
def update_games_table_with_dates(df_dates):
    try:
        logging.info(f"Processing {len(df_dates)} extracted dates.")

        with engine.connect() as connection:
            # Check if date_time column exists
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'games'
                    AND column_name = 'date_time'
                );
            """)).scalar()

            if not result:
                connection.execute(text("""
                    ALTER TABLE games
                    ADD COLUMN date_time DATE;
                """))
                connection.commit()
                logging.info("date_time column added to games table.")
            else:
                logging.info("date_time column already exists in games table.")

            # Update games table with date_time from DataFrame
            for _, row in df_dates.iterrows():
                game_id = row['game_id']
                date_time = row['date_time']
                connection.execute(text("""
                    UPDATE games
                    SET date_time = :date_time
                    WHERE game_id = :game_id;
                """), {"date_time": date_time, "game_id": game_id})
            connection.commit()

        logging.info("Successfully updated games table with date_time data.")

    except Exception as e:
        logging.error(f"Error updating database: {e}")

def main():
    # Get Chess.com username from command-line argument
    if len(sys.argv) > 1:
        player = sys.argv[1].strip().lower()
    else:
        player = input("Enter the Chess.com username: ").strip().lower()

    # Step 1: Process JSON files and extract dates into a DataFrame
    dates_df = process_json_files_for_dates(player)

    # Step 2: Update the database with the extracted dates
    if not dates_df.empty:
        update_games_table_with_dates(dates_df)
    else:
        logging.error(f"No valid dates found for {player} to update the database.")

if __name__ == "__main__":
    main()