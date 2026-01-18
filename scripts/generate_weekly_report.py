import json
import pandas as pd
from pathlib import Path
import sys
import argparse
from datetime import datetime

def load_data(week, season):
    file_path = f'output_data/week{week}_payload.json'
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found. Please ensure the payload for Week {week} has been extracted.")
        sys.exit(1)

def format_currency(value):
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:+.2f}"

def format_percent(value):
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.1%}"

def format_value(value):
    if value is None or pd.isna(value):
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)

def generate_markdown_report(games, week, season, output_file):
    md = []
    md.append(f"# NFELO Week {week} Report (Season {season})\n")
    md.append(f"**Total Games Analysis:** {len(games)}\n")
    
    for game in games:
        # Filter for season
        game_season = game.get('season')
        if game_season and int(game_season) != season:
            continue

        home_team = game.get('home_team')
        away_team = game.get('away_team')
        gameday = game.get('gameday')
        gametime = game.get('gametime')
        game_id = game.get('game_id')
        
        # Core Metrics
        home_prob = game.get('nfelo_home_probability_close')
        away_prob = 1 - home_prob if home_prob else None
        home_elo = game.get('home_nfelo_elo')
        away_elo = game.get('away_nfelo_elo')
        home_qb = game.get('home_538_qb')
        away_qb = game.get('away_538_qb')
        home_ev = game.get('home_ev')
        away_ev = game.get('away_ev')
        home_ml = game.get('home_ml_close')
        away_ml = game.get('away_ml_close')
        home_ats_pct = game.get('home_ats_pct')

        # Header
        md.append(f"## {away_team} @ {home_team}")
        md.append(f"**Time:** {gameday} at {gametime} | **ID:** `{game_id}`\n")

        # Matchup Table
        md.append("| Metric | Home (**" + str(home_team) + "**) | Away (**" + str(away_team) + "**) |")
        md.append("| :--- | :--- | :--- |")
        md.append(f"| **Quarterback** | {home_qb} | {away_qb} |")
        md.append(f"| **NFELO Rating** | {home_elo:.1f} | {away_elo:.1f} |")
        md.append(f"| **Win Prob** | {format_percent(home_prob)} | {format_percent(away_prob)} |")
        md.append(f"| **Moneyline** | {home_ml} | {away_ml} |")
        md.append(f"| **Betting EV** | **{format_currency(home_ev)}** | **{format_currency(away_ev)}** |")
        md.append("")

        # Betting Signal Callout
        if home_ev and home_ev > 0:
            md.append(f"> 🟢 **BETTING SIGNAL:** Value detected on **{home_team}** (EV: {format_currency(home_ev)})")
        elif away_ev and away_ev > 0:
            md.append(f"> 🟢 **BETTING SIGNAL:** Value detected on **{away_team}** (EV: {format_currency(away_ev)})")
        else:
            md.append(f"> ⚪ **BETTING SIGNAL:** No significant edge detected.")
        
        md.append(f"\n**Market Sentiment:** {format_percent(home_ats_pct)} of tickets on {home_team} spread.\n")

        # Data Breakdown (Collapsible)
        md.append("<details>")
        md.append("<summary><strong>Click to expand full data breakdown</strong></summary>\n")
        md.append("| Data Point | Value |")
        md.append("| :--- | :--- |")
        
        exclude_keys = ['game_id', 'season', 'week', 'home_team', 'away_team', 'gameday', 'gametime']
        sorted_keys = sorted([k for k in game.keys() if k not in exclude_keys])
        
        for k in sorted_keys:
            md.append(f"| `{k}` | {format_value(game.get(k))} |")
            
        md.append("\n</details>\n")
        md.append("---\\n")

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))
    
    print(f"Success! Report generated at: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate NFELO Weekly Report')
    parser.add_argument('week', type=int, help='Week number to generate report for')
    parser.add_argument('--season', type=int, default=2025, help='Season year (default: 2025)')
    
    args = parser.parse_args()
    
    data = load_data(args.week, args.season)
    output_filename = f"output_data/week{args.week}_report.md"
    generate_markdown_report(data, args.week, args.season, output_filename)
