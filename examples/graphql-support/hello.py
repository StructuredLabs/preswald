from preswald import connect, get_df, table, text


text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Initialize connection (loads data sources as defined in preswald.toml)
connect()

# Load the GraphQL data source (using the 'countries' key from your config)
df = get_df("countries")

# Display a title and explanation about GraphQL integration
text(
    "# Countries Data\n\n"
    "This example demonstrates how GraphQL is implemented in Preswald. "
    "The query is defined inline in the preswald.toml file, fetching data from a public Countries API. "
    "The nested JSON response is automatically flattened into a simple DataFrame for display."
)

# Display the resulting data in a table
table(df, title="Countries")
