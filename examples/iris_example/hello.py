from preswald import connect, get_df, table, text, slider, plotly
import plotly.express as px
import pandas as pd
import os

# App header
text("# 🌸 Iris Dataset Explorer")
text("Analyzing the classic Iris flower dataset")
text("## Data Loading")

try:
    connect()
    df = None
    possible_names = ['iris', 'iris.csv', 'Iris', 'iris_data']
    for name in possible_names:
        try:
            df = get_df(name)
            if df is not None and len(df) > 0:
                text(f"✅ Successfully loaded dataset from source: '{name}'")
                break
        except Exception:
            continue

    if df is None:
        text("Attempting to load iris.csv directly from the data directory...")
        possible_paths = ['data/iris.csv', './data/iris.csv', '../data/iris.csv', 'iris.csv']
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    df = pd.read_csv(path)
                    text(f"✅ Successfully loaded Iris dataset from: {path}")
                    break
                except Exception as e:
                    text(f"Error loading from {path}: {str(e)}")

    if df is None:
        text("⚠️ Could not load the Iris dataset. Creating sample data for demonstration.")
        df = pd.DataFrame({
            'sepal_length': [5.1, 4.9, 4.7, 7.0, 6.4, 6.9, 6.3, 6.5, 7.6],
            'sepal_width': [3.5, 3.0, 3.2, 3.2, 3.2, 3.1, 3.3, 2.8, 3.0],
            'petal_length': [1.4, 1.4, 1.3, 4.7, 4.5, 4.9, 6.0, 5.1, 6.6],
            'petal_width': [0.2, 0.2, 0.2, 1.4, 1.5, 1.5, 2.5, 1.9, 2.1],
            'species': ['setosa', 'setosa', 'setosa', 'versicolor', 'versicolor', 'versicolor', 'virginica', 'virginica', 'virginica']
        })

    # Standardize column names
    if 'sepal.length' in df.columns:
        df = df.rename(columns={
            'sepal.length': 'sepal_length',
            'sepal.width': 'sepal_width',
            'petal.length': 'petal_length',
            'petal.width': 'petal_width'
        })
    if 'variety' in df.columns and 'species' not in df.columns:
        df = df.rename(columns={'variety': 'species'})
    if 'class' in df.columns and 'species' not in df.columns:
        df = df.rename(columns={'class': 'species'})

    # Display dataset information
    text("## Dataset Overview")
    text(f"The dataset contains {len(df)} flowers with {len(df.columns)} features.")
    text("### Preview")
    table(df.head(5), title="First 5 samples")
    text("### Summary Statistics")
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        stats_df = df[numeric_cols].describe().round(2)
        table(stats_df, title="Statistical Summary")
    
    # Interactive data exploration
    text("## Interactive Data Exploration")
    if 'species' in df.columns:
        species_counts = df['species'].value_counts().reset_index()
        species_counts.columns = ['Species', 'Count']
        table(species_counts, title="Flowers by Species")
        
        text("### Sepal Dimensions by Species")
        if 'sepal_length' in df.columns and 'sepal_width' in df.columns:
            fig1 = px.scatter(
                df,
                x='sepal_length',
                y='sepal_width',
                color='species',
                title="Sepal Length vs Width",
                labels={
                    'sepal_length': 'Sepal Length (cm)',
                    'sepal_width': 'Sepal Width (cm)',
                    'species': 'Species'
                }
            )
            plotly(fig1)
        
        text("### Petal Dimensions by Species")
        if 'petal_length' in df.columns and 'petal_width' in df.columns:
            fig2 = px.scatter(
                df,
                x='petal_length',
                y='petal_width',
                color='species',
                title="Petal Length vs Width",
                labels={
                    'petal_length': 'Petal Length (cm)',
                    'petal_width': 'Petal Width (cm)',
                    'species': 'Species'
                }
            )
            plotly(fig2)
    
    # Filter by sepal length
    if 'sepal_length' in df.columns:
        text("### Filter by Sepal Length")
        min_length = float(df['sepal_length'].min())
        max_length = float(df['sepal_length'].max())
        default_length = min_length + (max_length - min_length) / 2
        sepal_length_threshold = slider(
            "Minimum Sepal Length (cm)",
            min_val=min_length,
            max_val=max_length,
            default=default_length
        )
        filtered_df = df[df['sepal_length'] >= sepal_length_threshold]
        text(f"Showing {len(filtered_df)} flowers with sepal length ≥ {sepal_length_threshold:.1f} cm")
        table(filtered_df, title="Filtered Results")

except Exception as e:
    text(f"⚠️ An error occurred: {str(e)}")
    text("Please check that the iris.csv file exists in your data directory.")

text("---")
text("Iris Dataset Explorer | Built with Preswald")
