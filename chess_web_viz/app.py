from flask import Flask, render_template
from sqlalchemy import create_engine
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot
import re
import sys  # Potentially for getting username from command line

app = Flask(__name__)

DB_URL = "postgresql://postgres:gharm@localhost:5432/chess_data"
engine = create_engine(DB_URL)

# Get player name from command-line or default
def get_default_player():
    if len(sys.argv) > 1:
        return sys.argv[1].strip().lower()
    else:
        return 'LOVEVAE'  # Or handle no input as needed

@app.route('/')
@app.route('/<username>')
def dashboard(username=None):
    if username is None:
        username = get_default_player()

    # --- Fetch Data ---
    query = f"""
    SELECT
        date_time,
        CASE WHEN white_player_id = '{username}' THEN white_rating ELSE black_rating END AS player_rating,
        white_player_id,
        white_rating,
        black_player_id,
        black_rating,
        winner,
        time_control,
        pgn,
        eco
    FROM games
    WHERE lower(white_player_id) = '{username.lower()}' OR lower(black_player_id) = '{username.lower()}'
    """
    df = pd.read_sql(query, engine)

    # --- Rating Over Time ---
    fig_rating_time = go.Figure(data=[go.Scatter(x=df['date_time'], y=df['player_rating'],
                                                 mode='lines+markers', name='Rating')])
    fig_rating_time.update_layout(title=f"{username}'s Rating Over Time", xaxis_title="Date Time", yaxis_title="Rating")
    plot_rating_time_div = plot(fig_rating_time, output_type='div', include_plotlyjs='cdn')

    # --- Rating Distribution ---
    white_ratings = df[df['white_player_id'].str.lower() == username.lower()]['white_rating'].dropna()
    black_ratings = df[df['black_player_id'].str.lower() == username.lower()]['black_rating'].dropna()
    fig_rating_dist = go.Figure()
    if not white_ratings.empty:
        fig_rating_dist.add_trace(go.Histogram(x=white_ratings, name='Rating as White'))
    if not black_ratings.empty:
        fig_rating_dist.add_trace(go.Histogram(x=black_ratings, name='Rating as Black'))
    fig_rating_dist.update_layout(title=f"{username}'s Rating Distribution (White vs. Black)", xaxis_title="Rating", yaxis_title="Frequency", barmode='overlay', bargap=0.2)
    fig_rating_dist.update_traces(opacity=0.75)
    plot_rating_dist_div = plot(fig_rating_dist, output_type='div', include_plotlyjs=False)

    # --- Win Rate White/Black ---
    total_white = df[df['white_player_id'].str.lower() == username.lower()].shape[0]
    wins_white = df[df['white_player_id'].str.lower() == username.lower()]['winner'].str.lower().eq(username.lower()).sum()
    total_black = df[df['black_player_id'].str.lower() == username.lower()].shape[0]
    wins_black = df[df['black_player_id'].str.lower() == username.lower()]['winner'].str.lower().eq(username.lower()).sum()
    win_rate_white = (wins_white / total_white) * 100 if total_white > 0 else 0
    win_rate_black = (wins_black / total_black) * 100 if total_black > 0 else 0
    fig_win_rate = go.Figure(data=[
        go.Bar(name='Win Rate as White', x=['White'], y=[win_rate_white]),
        go.Bar(name='Win Rate as Black', x=['Black'], y=[win_rate_black])
    ])
    fig_win_rate.update_layout(title=f"{username}'s Win Rate (White vs. Black)", yaxis_title="Win Rate (%)")
    plot_win_rate_div = plot(fig_win_rate, output_type='div', include_plotlyjs=False)

    # --- Rating by Time Control ---
    df_filtered_tc = df[df['player_rating'].notna()]
    fig_rating_tc = go.Figure()
    for control in df_filtered_tc['time_control'].unique():
        subset = df_filtered_tc[df_filtered_tc['time_control'] == control]
        fig_rating_tc.add_trace(go.Box(y=subset['player_rating'], name=control))
    fig_rating_tc.update_layout(title=f"{username}'s Rating Distribution by Time Control", xaxis_title="Time Control", yaxis_title="Rating")
    plot_rating_tc_div = plot(fig_rating_tc, output_type='div', include_plotlyjs=False)

    # --- ECO Performance ---
    eco_stats = df.groupby('eco')['winner'].agg(
        total_games='count',
        wins=lambda x: (x.str.lower() == username.lower()).sum()
    ).reset_index()
    eco_stats['win_rate'] = eco_stats['wins'] / eco_stats['total_games']
    filtered_eco_stats = eco_stats[eco_stats['total_games'] >= 25].sort_values(by='win_rate', ascending=False).head(10)

    fig_eco = go.Figure()
    if not filtered_eco_stats.empty:
        fig_eco.add_trace(go.Bar(x=filtered_eco_stats['eco'], y=filtered_eco_stats['win_rate'], name='Win Rate'))
        fig_eco.add_trace(go.Scatter(x=filtered_eco_stats['eco'], y=filtered_eco_stats['total_games'] / filtered_eco_stats['total_games'].max(),
                                  mode='lines+markers', name='Games Played (Scaled)', yaxis='y2'))
        fig_eco.update_layout(yaxis2=dict(title="Games Played (Scaled)", overlaying='y', side='right'))
    fig_eco.update_layout(title=f"{username}'s Top ECO Performance (>= 25 Games)", xaxis_title="ECO Code", yaxis_title="Win Rate")
    plot_eco_div = plot(fig_eco, output_type='div', include_plotlyjs=False)

    return render_template('dashboard.html',
                           username=username,
                           plot_rating_time_div=plot_rating_time_div,
                           plot_rating_dist_div=plot_rating_dist_div,
                           plot_win_rate_div=plot_win_rate_div,
                           plot_rating_tc_div=plot_rating_tc_div,
                           plot_eco_div=plot_eco_div)

if __name__ == '__main__':
    app.run(debug=True)