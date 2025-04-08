import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys
import re
import requests
import chess.pgn

# Database connection
DB_URL = "postgresql://postgres:gharm@localhost:5432/chess_data"
engine = create_engine(DB_URL)

# Get player name from command-line or terminal input
if len(sys.argv) > 1:
    PLAYER_NAME = sys.argv[1].strip().lower()
    print(f"Analyzing data for player: {PLAYER_NAME} (from command line)")
else:
    PLAYER_NAME = input("Enter the Chess.com username to analyze: ").strip().lower()
    print(f"Analyzing data for player: {PLAYER_NAME} (entered in terminal)")

# Query to fetch relevant data for the input player (white or black)
query = f"""
SELECT
    white_player_id,
    white_rating,
    black_player_id,
    black_rating,
    winner,
    date_time,
    time_control,
    pgn
FROM games
WHERE LOWER(white_player_id) = '{PLAYER_NAME}' OR LOWER(black_player_id) = '{PLAYER_NAME}'
"""

df_player = pd.read_sql(query, engine)

if df_player.empty:
    print(f"Warning: No games found in the database for player '{PLAYER_NAME}'.")
    sys.exit(1)

# Convert date_time to datetime and sort
df_player['date_time'] = pd.to_datetime(df_player['date_time'])
df_player = df_player.sort_values(by='date_time')

# Add player's rating column (based on whether they were playing white or black)
df_player['player_rating'] = df_player.apply(
    lambda row: row['white_rating'] if row['white_player_id'].lower() == PLAYER_NAME else row['black_rating'],
    axis=1
)

# Plot the player's rating over time
plt.figure(figsize=(14, 7))
plt.plot(df_player['date_time'], df_player['player_rating'], marker='o', linestyle='-', color='b')
plt.title(f"{PLAYER_NAME}'s Rating Over Time")
plt.xlabel("Date Time")
plt.ylabel(f"{PLAYER_NAME}'s Rating")
plt.grid(True)
plt.tight_layout()
plt.show()

# Check the first few rows of the dataframe
print(df_player.head())

# Count the number of games the player played
total_player_games = len(df_player)

# Count the number of games the player won
player_wins = df_player.apply(
    lambda row: 1 if str(row['winner']).lower() == PLAYER_NAME else 0, axis=1
).sum()

# Calculate the player's win rate
player_win_rate = player_wins / total_player_games if total_player_games > 0 else 0

print(f"{PLAYER_NAME}'s Total Games: {total_player_games}")
print(f"{PLAYER_NAME}'s Wins: {player_wins}")
print(f"{PLAYER_NAME}'s Win Rate: {player_win_rate * 100:.2f}%")

# Create two subplots: one for white player ratings, another for black player ratings
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

white_games = df_player[df_player['white_player_id'].str.lower() == PLAYER_NAME]
sns.histplot(white_games['white_rating'], kde=True, ax=axes[0], color='blue', bins=30, alpha=0.7)
axes[0].set_title(f"{PLAYER_NAME}'s Rating as White Player")
axes[0].set_xlabel("Rating")
axes[0].set_ylabel("Frequency")

# Plot for the player's rating as Black
black_games = df_player[df_player['black_player_id'].str.lower() == PLAYER_NAME]
sns.histplot(black_games['black_rating'], kde=True, ax=axes[1], color='red', bins=30, alpha=0.7)
axes[1].set_title(f"{PLAYER_NAME}'s Rating as Black Player")
axes[1].set_xlabel("Rating")
axes[1].set_ylabel("Frequency")

# Adjust layout
plt.tight_layout()
plt.show()

# Count the number of games the player played as White and Black
total_white_games = len(df_player[df_player['white_player_id'].str.lower() == PLAYER_NAME])
total_black_games = len(df_player[df_player['black_player_id'].str.lower() == PLAYER_NAME])

# Count the number of games the player won as White and Black
player_wins_white = df_player[df_player['white_player_id'].str.lower() == PLAYER_NAME].apply(
    lambda row: 1 if str(row['winner']).lower() == PLAYER_NAME else 0, axis=1
).sum()

player_wins_black = df_player[df_player['black_player_id'].str.lower() == PLAYER_NAME].apply(
    lambda row: 1 if str(row['winner']).lower() == PLAYER_NAME else 0, axis=1
).sum()

# Calculate the player's win rate when playing as White and Black
win_rate_white = player_wins_white / total_white_games if total_white_games > 0 else 0
win_rate_black = player_wins_black / total_black_games if total_black_games > 0 else 0

# Calculate the player's overall win rate (same as before)
overall_win_rate = player_wins / total_player_games if total_player_games > 0 else 0

# Print win rates
print(f"{PLAYER_NAME}'s Total Games: {total_player_games}")
print(f"{PLAYER_NAME}'s Total Wins: {player_wins}")
print(f"{PLAYER_NAME}'s Overall Win Rate: {overall_win_rate * 100:.2f}%")
print(f"{PLAYER_NAME}'s Win Rate as White: {win_rate_white * 100:.2f}%")
print(f"{PLAYER_NAME}'s Win Rate as Black: {win_rate_black * 100:.2f}%")

# Now, plot the win rates for White and Black
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot for player's win rate when playing as White
axes[0].bar(['White'], [win_rate_white], color='blue')
axes[0].set_title(f"{PLAYER_NAME}'s Win Rate as White Player")
axes[0].set_ylabel("Win Rate")
axes[0].set_ylim(0, 1)

# Plot for player's win rate when playing as Black
axes[1].bar(['Black'], [win_rate_black], color='red')
axes[1].set_title(f"{PLAYER_NAME}'s Win Rate as Black Player")
axes[1].set_ylabel("Win Rate")
axes[1].set_ylim(0, 1)

# Adjust layout
plt.tight_layout()
plt.show()

# 1. Time Control Distribution (Rating vs Time Control)
plt.figure(figsize=(10, 6))
sns.boxplot(data=df_player, x='time_control', y='player_rating') # Using player_rating for consistency
plt.title(f"{PLAYER_NAME}'s Rating Distribution by Time Control")
plt.xlabel("Time Control")
plt.ylabel("Rating")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Performance by ECO Code (filtered by play count)
def extract_eco(pgn):
    """ Extract the ECO code from the PGN, if available. """
    eco_match = re.search(r'\[ECO\s+"(.*?)"\]', pgn)
    return eco_match.group(1) if eco_match else "Unknown"

df_player['eco'] = df_player['pgn'].apply(extract_eco)

# Add a column for win or loss based on the game result
df_player['result'] = df_player.apply(
    lambda row: 'win' if str(row['winner']).lower() == PLAYER_NAME else 'loss', axis=1
)

# Group by ECO code and calculate win rate and games played
eco_stats = df_player.groupby('eco')['result'].agg(
    win_rate=lambda x: (x == 'win').mean(),
    games_played='count'
).reset_index()

# Filter out ECO codes played less than 25 times
filtered_eco_stats = eco_stats[eco_stats['games_played'] >= 25]

# Sort by win rate (descending) for better visualization
filtered_eco_stats_sorted = filtered_eco_stats.sort_values(by='win_rate', ascending=False)

# Plot the win rate and games played by ECO code (filtered)
fig, ax1 = plt.subplots(figsize=(12, 8))

if not filtered_eco_stats_sorted.empty:
    sns.barplot(data=filtered_eco_stats_sorted, x='eco', y='win_rate', palette='viridis', ax=ax1)
    ax1.set_title(f"{PLAYER_NAME}'s Performance by ECO Code (>= 25 Games)")
    ax1.set_xlabel("ECO Code")
    ax1.set_ylabel("Win Rate")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)

    # Create a second axis to plot the number of games played
    ax2 = ax1.twinx()
    sns.lineplot(data=filtered_eco_stats_sorted, x='eco', y='games_played', color='r', ax=ax2, marker='o', linewidth=2)
    ax2.set_ylabel("Games Played", color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    # Display the plot
    plt.tight_layout()
    plt.show()
else:
    print(f"No ECO codes played at least 25 times found for {PLAYER_NAME}.")