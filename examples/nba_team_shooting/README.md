# NBA Shot Analysis  

## Overview  
An interactive dashboard analyzing NBA shot location data, built with Preswald. Users can explore shooting efficiency by player, team, and shot type.  

## Dataset Source  
- **NBA API – Shot Chart Detail**  
  [Source](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/shotchartdetail.md)  
- Includes shot attempts, makes, locations, players, teams, and shot types.  

## Features  
- **Player & Team Selection** – Filter by specific players or teams.  
- **Shooting Statistics** – Total shots, makes, and shooting percentage.  
- **Shot Zone Breakdown** – Efficiency by court zones.  
- **Shot Type Breakdown** – Analyzes different shot types (e.g., layups, jump shots).  
- **Interactive Shot Chart** – Visualizes made (green) and missed (red) shots.  
- **Full Dataset View** – Displays raw shot data for reference.  

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`