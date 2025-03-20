# Formula 1 Hub

## Dataset Source
This project uses Formula 1 data accessed via Preswald’s `connect()` and `get_df()` functions. The datasets include:
- `races_csv`: Race details (year, circuitId, raceId).
- `results_csv`: Race results (driverId, positionOrder).
- `circuits_csv`: Circuit info (circuitId, name).
- `lap_times_csv`: Lap times (driverId, milliseconds).
- `drivers_csv`: Driver details (driverId, forename, surname).

## What the App Does
The `f1_hub.py` script creates an interactive Formula 1 dashboard:
1. A slider selects from the top 15 circuits (by race count) from 2015–2024 (a commented-out selectbox is available as an alternative).
2. Displays a table and bar chart of drivers with the most wins at the selected circuit.
3. Shows a table and scatter plot of the top 10 average lap times.

It uses Pandas for data manipulation, Plotly for charts, and Preswald’s UI tools (`slider`, `table`, `plotly`).