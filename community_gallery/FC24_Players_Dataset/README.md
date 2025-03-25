# ⚽ FC 24 Player Stats Explorer

An interactive data exploration app built with [Preswald](https://preswald.ai/) that visualizes player statistics from **FC 24**. Explore players by overall rating, position, age, and club — all in an elegant browser-based dashboard.

---
## Live link to assignment
https://fc24-stats-explorer-upm8riuf.preswald.app/

## Dataset Source

The dataset is based on player statistics from **FC 24 (FIFA 24)** and includes:

- Player name, age, nationality, and club
- Overall rating, position, and detailed attributes (pace, shooting, passing, etc.)
- Physical stats like height, weight, work rates, and more

**Original file:** `all_fc_24_players.csv`  
**Trimmed file for deployment:** `all_fc_24_players_small.csv` (top 1000 rows)

> The full dataset was trimmed to reduce deployment size and ensure fast performance.

---

## What the App Does

- Displays a preview of top players
- Lets users **filter players** by overall rating using a slider
- Shows an interactive **scatter plot** of `Overall Rating` vs `Age` grouped by position
- Hover to view player's **name, club, and nationality**

### Features
- Slider-controlled filtering
- Dynamic data table with live updates
- Interactive Plotly chart
- Clean and responsive UI using Preswald's components

---

## 🛠️ How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/shubhamchoudhar/fc24-stats-explorer.git
cd fc24-stats-explorer
