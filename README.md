♟️ Chess Players Statistics
A comprehensive data pipeline designed to process, analyze, and visualize Chess.com game data for individual players.

📂 Project Structure
.
├── chess-analytics-poland/       # Data analysis scripts and notebooks
├── chess_env/                    # Environment setup and dependencies
├── chess_web_viz/                # Web-based visualization components
├── data/                         # Data processing scripts and resources
├── .gitignore                    # Git ignore file
├── database_creation_query       # SQL scripts for database setup
├── opening_names.csv             # CSV file containing chess opening names
└── requirements.txt              # Python dependencies

⚙️ Setup Instructions

1. Clone the Repository
git clone https://github.com/GharmMDS/Chess-Players-Statistics.git
cd Chess-Players-Statistics

2. Set Up the Environment
Ensure you have Python installed. It's recommended to use a virtual environment:
python -m venv chess_env source chess_env/bin/activate  # On Windows, use 'chess_env\Scripts\activate'

4. Install Dependencies
pip install -r requirements.txt

4. Configure the Database
Set up a PostgreSQL database named chess_data. Update the database connection settings in the relevant scripts to match your configuration.

5. Prepare Game Data
Obtain your Chess.com game data in JSON format and place it in the appropriate directory, ensuring the filenames follow the expected naming convention.

🚀 Running the Pipeline
Execute the main script to run the entire data processing and analysis pipeline:
python main.py

📊 Features
Data Extraction: Parses Chess.com game data in PGN format to extract relevant information.

Database Integration: Stores processed data into a PostgreSQL database for efficient querying.

Statistical Analysis: Computes various statistics, such as average player ratings and win rates.

Visualization: Provides tools for visualizing player performance metrics over time.

📈 Analysis & Visualization
This project goes beyond simple data collection. It includes in-depth statistical analysis and visualization tools to gain insights from Chess.com game history:

🔍 Analysis Highlights (analyze_data.py)
Average Rating Pairings: Understand the average ratings of players against specific opponents.

Games Played: View total games played by each player, separated into white and black pieces.

Win Rates: Calculate win percentages across all games and detect player performance trends.

Example output: 
🎯 Average Ratings Per Player Pairing:
  white_player_id  avg_white_rating  black_player_id  avg_black_rating
0          player1           1450.2          player2           1475.6

🎯 Total Games Played Per Player (White & Black):
  player_id  white_games  black_games  total_games
0   player1           50           60          110

🎯 Win Rates Per Player:
  player_id  win_rate
0   player1      0.57

📊 Visualization (visualize.py)
The project includes optional visualizations to explore game trends:

📆 Activity Over Time: See when players are most active.

♟️ Opening Popularity: Visualize the most commonly played openings.

📉 Rating Progression: Observe how player ratings have changed over time.

Note: Visualizations are CLI-based, but the project is modular for future web-based dashboards.

🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your enhancements.

🛡️ License
This project is licensed under the MIT License. See the LICENSE file for more details.