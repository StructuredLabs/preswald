import numpy as np
import pandas as pd
import plotly.express as px
from preswald import plotly, text

# 1. Dashboard Title and Description
text("# Analyzing Pixar Films Data")
text("Exploring various aspects of Pixar films, including box office performance, ratings, and correlations.")

# Load dataset
df = pd.read_csv("data/pixar_movies.csv")

# 2. Box Office Earnings by Film
fig1 = px.bar(
    df,
    x="film",
    y="box_office_worldwide",
    title="Box Office Earnings by Film",
    labels={"film": "Film", "box_office_worldwide": "Worldwide Box Office ($)"},
    template="plotly_white",
)
plotly(fig1)

# 3. Rotten Tomatoes Score Over Time
df["release_date"] = pd.to_datetime(df["release_date"])
df = df.sort_values("release_date")
df["release_date"] = df["release_date"].dt.strftime("%Y-%m-%d")
fig2 = px.line(
    df,
    x="release_date",
    y="rotten_tomatoes_score",
    title="Rotten Tomatoes Score Over Time",
    labels={"release_date": "Release Year", "rotten_tomatoes_score": "Rotten Tomatoes Score"},
    template="plotly_white",
)
plotly(fig2)

# 4. Budget vs. Worldwide Box Office Scatter Plot
fig3 = px.scatter(
    df,
    x="budget",
    y="box_office_worldwide",
    title="Budget vs. Worldwide Box Office",
    labels={"budget": "Budget ($)", "box_office_worldwide": "Worldwide Box Office ($)"},
    template="plotly_white",
)
plotly(fig3)

# 5. Distribution of Film Ratings
ratings_count = df["film_rating"].value_counts()
fig4 = px.pie(
    names=ratings_count.index,
    values=ratings_count.values,
    title="Distribution of Film Ratings",
)
plotly(fig4)

# 6. IMDb Scores Distribution
fig5 = px.histogram(
    df,
    x="imdb_score",
    nbins=10,
    title="Distribution of IMDb Scores",
    labels={"imdb_score": "IMDb Score"},
    template="plotly_white",
)
plotly(fig5)

# 7. Box Office Earnings Distribution
fig6 = px.box(
    df,
    y="box_office_worldwide",
    title="Box Office Earnings Distribution",
    labels={"box_office_worldwide": "Worldwide Box Office ($)"},
    template="plotly_white",
)
plotly(fig6)

# 8. Correlation Heatmap
fig7 = px.imshow(
    df.select_dtypes(include=["number"]).corr(),  # Only numeric columns
    labels={"x": "Variables", "y": "Variables", "color": "Correlation"},
    title="Correlation Between Variables",
    color_continuous_scale="Viridis",
)
plotly(fig7)

text("This dashboard provides insights into Pixar films, analyzing financial performance and critical reception through interactive visualizations.")
