from preswald import (connect, get_df, table, slider, plotly)
import plotly.express as px

# Load the CSV
connect()
df = get_df('pixar_films')

# Display all films
table(df, "All Pixar Films")

# Filter films by imdb_score
imdb_threshold = slider("imdb score", min_val = 0, max_val = 10)
table(df[df['imdb_score'] >= imdb_threshold][['ID', 'film', 'imdb_score']], "Filter Pixar Films by imdb_score")

# Filter films by rotten_tomatoes_score
rt_threshold = slider("rotten tomatoes score", min_val = 30, max_val = 100)
table(df[df['rotten_tomatoes_score'] >= rt_threshold][['ID', 'film', 'rotten_tomatoes_score']], "Filter Pixar Films by rotten_tomatoes_score")


# Group films by film rating
rating_counts = df['film_rating'].value_counts().reset_index()
rating_counts.columns = ['film_rating', 'count']
fig = px.pie(rating_counts, values='count', names = "film_rating", title="Film Ratings of Pixar Films")
plotly(fig)
