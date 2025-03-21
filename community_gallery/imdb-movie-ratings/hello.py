import pandas as pd
import plotly.express as px
from preswald import text, plotly, connect, get_df, table, selectbox, slider

text("## 🎥 **Movie Explorer: Ratings, Trends & Fun Facts!** 🍿✨  \n"
     "### *A Deep Dive into Movie Ratings, Trends, and Surprising Insights!* 🚀")

connect()
df = get_df('movies_csv').dropna()

df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)
df["rating"] = df["rating"].astype(float)

unique_genres = set()
df["genres"].str.split(";").apply(unique_genres.update)
unique_genres = sorted(unique_genres)
unique_genres.insert(0, "All")

df["first_letter"] = df["name"].str[0].str.upper()
unique_letters = sorted(df["first_letter"].dropna().unique())
unique_letters.insert(0, "All")

filter_mode = selectbox("Filter By", options=["Genre", "Movie Name"], default="Genre")

if filter_mode == "Genre":
    text("You can type to search for a genre.")
    selected_genre = selectbox("Choose a Genre", options=unique_genres, default="All")  
    selected_letter = None
else:
    text("You can type to search for a letter.")
    selected_letter = selectbox("Choose a Starting Letter", options=unique_letters, default="All")  
    selected_genre = None

selected_rating = slider("Select Maximum Rating", min_val=1, max_val=10, default=10) 
min_year, max_year = int(df["year"].min()), int(df["year"].max())
selected_year = slider("Select Maximum Year", min_val=min_year, max_val=max_year, default=max_year)

selected_rating = int(selected_rating)
selected_year = int(selected_year)

def filter_movies(filter_mode, selected_genre, selected_letter, selected_rating, selected_year):
    filtered = df[(df['rating'] <= selected_rating) & (df['year'] <= selected_year)]
    
    if filter_mode == "Genre" and selected_genre != "All":
        filtered = filtered[filtered['genres'].str.contains(selected_genre, na=False, case=False)]
    elif filter_mode == "Movie Name" and selected_letter != "All":
        filtered = filtered[filtered['first_letter'] == selected_letter]
    
    filtered = filtered.drop_duplicates(subset=['name'], keep='first')
    return filtered.astype(object) if not filtered.empty else pd.DataFrame(columns=['name', 'genres', 'year', 'rating', 'num_raters', 'num_reviews', 'run_length'])

filtered_df = filter_movies(filter_mode, selected_genre, selected_letter, selected_rating, selected_year)[['name', 'genres', 'year', 'rating', 'num_raters', 'num_reviews', 'run_length']]

display_df = filtered_df.rename(columns={
    "name": "Movie Name",
    "genres": "Genres",
    "year": "Release Year",
    "rating": "Rating",
    "num_raters": "Number of Raters",
    "num_reviews": "Number of Reviews",
    "run_length": "Duration"
})

text(f"Number of movies: {len(display_df)}")
table(display_df)

movies_per_year = df.groupby("year").size().reset_index(name="count")
average_rating_per_year = df.groupby("year")["rating"].mean().reset_index()

text("Number of Movies Released Per Year")
fig1 = px.line(
    movies_per_year, 
    x="year", 
    y="count", 
    markers=True,
    labels={"year": "Year", "count": "Number of Movies Released"}
)
fig1.update_layout(
    autosize=False,
    width=900,
    height=500,
    margin=dict(l=50, r=50, t=50, b=50),
    xaxis_title="Year",  
    yaxis_title="Number of Movies Released"
)
plotly(fig1)

text("Average Movie Rating Per Year")
fig2 = px.line(
    average_rating_per_year, 
    x="year", 
    y="rating", 
    markers=True,
    labels={"year": "Year", "rating": "Average Rating"}
)
fig2.update_layout(
    autosize=False,
    width=900,
    height=500,
    margin=dict(l=50, r=50, t=50, b=50),
    xaxis_title="Year",  
    yaxis_title="Average Rating"
)
plotly(fig2)

text("Duration vs Average Rating")
unique_run_length_df = df.groupby("run_length", as_index=False)["rating"].mean()

fig3 = px.scatter(
    unique_run_length_df, 
    x="run_length", 
    y="rating", 
    labels={"run_length": "Run Length (Minutes)", "rating": "Average Rating"},
    opacity=0.6
)
fig3.update_layout(
    autosize=False,
    width=900,
    height=500,
    margin=dict(l=50, r=50, t=50, b=50),
    xaxis_title="Run Length (Minutes)",  
    yaxis_title="Average Rating"
)
plotly(fig3)


text("🎬 **Fun Movie Facts!** 🎬")

selected_fact = selectbox(
    "Pick a movie fact to reveal!", 
    options=[
        "⭐ Highest-Rated Movie", 
        "💀 Lowest-Rated Movie", 
        "🎥 Longest Movie", 
        "⏳ Shortest Movie", 
        "👥 Most Rated Movie", 
        "🕵️‍♂️ Least Rated Movie", 
        "📜 Earliest Released Movie", 
        "🚀 Latest Released Movie"
    ],
    default=None
)

if selected_fact == "⭐ Highest-Rated Movie":
    text("🎥 **The Shawshank Redemption** - 📊 Rating: **9.3**")

elif selected_fact == "💀 Lowest-Rated Movie":
    text("🎥 **Spice World** - 📊 Rating: **3.5**")

elif selected_fact == "🎥 Longest Movie":
    text("🎬 **Gettysburg** - ⏳ Runtime: **271 minutes**")

elif selected_fact == "⏳ Shortest Movie":
    text("🎬 **Battleship Potemkin** - ⏳ Runtime: **66 minutes**")

elif selected_fact == "👥 Most Rated Movie":
    text("🎥 **The Shawshank Redemption** - 👥 Raters: **2,258,845**")

elif selected_fact == "🕵️‍♂️ Least Rated Movie":
    text("🎥 **The Alamo** - 👥 Raters: **19,290**")

elif selected_fact == "📜 Earliest Released Movie":
    text("🎥 **The Birth of a Nation** - 📅 Year: **1915**")

elif selected_fact == "🚀 Latest Released Movie":
    text("🎥 **Eurovision Song Contest: The Story of Fire Saga** - 📅 Year: **2020**")