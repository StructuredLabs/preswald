from preswald import text, plotly, connect, get_df, table, query,slider, selectbox
import pandas as pd
import plotly.express as px


text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('IMDb_csv')

if df is None or df.empty:
    text("DataFrame is empty. Check if the CSV is loaded correctly.")


# Extract unique genres (ensure format compatibility)
all_genres = ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Thriller", "Romance", "Adventure"]
selected_genre = selectbox("Select Genre", options=all_genres, default="Thriller")

# SQL Query to filter by the selected genre
sql = f"SELECT Budget, Home_Page, Movie_Name, Genres FROM IMDb_csv WHERE Genres LIKE '%{selected_genre}%'"

filtered_df = query(sql, "IMDb_csv")

if filtered_df is None or filtered_df.empty:
    text(f"No movies found in the **{selected_genre}** genre.")
else:
    text(f"## Movies in {selected_genre} Genre")
    table(filtered_df, title=f"Filtered Movies: {selected_genre}")

threshold = slider("Minimum Vote Average", min_val=0, max_val=10, default=5)

if "Vote_Average" in df.columns:
    df["Vote_Average"] = pd.to_numeric(df["Vote_Average"], errors="coerce") 
    filtered_votes_df = df[df["Vote_Average"] >= threshold]
    
    selected_columns = ["Budget", "Home_Page", "Movie_Name", "Genres", "Vote_Average", "Vote_Count"]
    filtered_votes_df = filtered_votes_df[selected_columns]

    table(filtered_votes_df, title="Movies Above Threshold")
else:
    text("Column 'Vote_Average' not found in DataFrame!")

# Scatter plot (Ensure required columns exist)
if all(col in df.columns for col in ["Vote_Average", "Vote_Count"]):
    df["Vote_Count"] = df["Vote_Count"].str.replace("K", "000").astype(float)  # Convert vote count
    fig = px.scatter(df, x="Vote_Average", y="Vote_Count", color="Movie_Name",
                     title="Vote Average vs. Vote Count")
    plotly(fig)
else:
    text("One or more columns for the plot are missing!")

