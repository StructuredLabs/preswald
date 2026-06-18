# League of Legends Champion Analysis Dashboard

An interactive dashboard for analyzing League of Legends champions' attributes, focusing on Blue Essence costs, roles, and various champion statistics.

## Dataset

The dataset contains information about League of Legends champions including:
- Champion names and API names
- Blue Essence costs
- Roles and range types
- Champion attributes (toughness, control, mobility)

## Features

1. **Interactive Filtering**
   - Slider to filter champions by Blue Essence cost
   - Dynamic table updates based on filter

2. **Visualizations**
   - Scatter plot comparing Blue Essence vs. Toughness
   - Violin plot showing Blue Essence distribution by range type
   - Density contour plot of Blue Essence vs. Control
   - Histogram of Blue Essence cost distribution by role

## How to Run

1. Install dependencies:
```bash
pip install preswald
```

2. Initialize the project:
```bash
preswald init lol_champion_analysis
cd lol_champion_analysis
```

3. Copy the data file to the `data/` directory

4. Update your `preswald.toml` to include the data source:
```toml
[data.lol_champions]
type = "csv"
path = "data/lol_champions.csv"
```

5. Run the app:
```bash
preswald run
```

## How to Deploy

Deploy to Structured Cloud:
```bash
preswald deploy --target structured
```

## Live Demo

You can view a live demo of this app at: [Your deployed app URL]

## Screenshots

[Add screenshots of your app here] 