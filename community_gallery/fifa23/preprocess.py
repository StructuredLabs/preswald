import pandas as pd


# Load the CSV file
file_path = "data/data.csv"
df = pd.read_csv(file_path)

# Fill missing values by median for each column
df = df.apply(lambda col: col.fillna(col.median()) if col.dtype != "O" else col, axis=0)

# Sort the DataFrame by 'Overall' rating in descending order
df_sorted = df.sort_values(by="Overall", ascending=False)

# Keep only the top 500 players
top_500_players = df_sorted.head(500)

# Save the modified DataFrame back to the same CSV file
top_500_players.to_csv(file_path, index=False)  # Overwrites the original file

# Print the modified dataframe to confirm
print(top_500_players.head())
