# NBA Stats season 2023-24

**[NBA Games Analytics Dashboard](https://nba-season-2023-24-767339-nl1igxu1-ndjz2ws6la-ue.a.run.app)**  
This [Dataset](https://drive.google.com/file/d/1Jfhs-qNx9rXxmvqUNmrbx0t2hksFUdU9/view?usp=sharing) comes from warehouse of my platform **[BetFlow](https://github.com/sanchitvj/sports_betting_analytics_engine)**.  


## Project Overview  
This application analyzes NBA game data stored in Snowflake warehouse (or loaded from CSV) to generate interactive visualizations using Plotly. It provides insights into team performance, game trends, venue statistics, and player leaders. Designed for sports analysts and basketball enthusiasts.

## Key Features
- **Score Comparisons**: Home vs. away team performance metrics (points, rebounds, assists).
- **Shooting Efficiency**: FG%, 3P%, and FT% analysis using radar charts.
- **Temporal Trends**: Game frequency and scores over time.
- **Venue Analytics**: Most active game locations.
- **Player Leaders**: Top performers in points, rebounds, and assists.

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`