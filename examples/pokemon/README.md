# Preswald Project
A web applicaition to visualize Pokèmon stats.

Data was sourced from [Pokédex for All 1025 Pokémon with Text Description](https://www.kaggle.com/datasets/rzgiza/pokdex-for-all-1025-pokemon-w-text-description)

- **Interactive Scatter Plot**:  
  Visualize the relationship between `Attack` and `Defense` stats.
- **Dynamic Data Filtering**:  
  Use the **slider** to adjust the attack threshold and view Pokémon with stats above the selected value.

- **Predefined SQL Queries**:  
  Example query to filter Pokémon with `Attack > 120` and `Defense > 100`.

- **Data Tables**:  
  View raw and filtered data

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`

## Deploy

1. Get an API key

2. Go to app.preswald.com
    Create a New Organization (top left corner)
    Navigate to Settings > API Keys
    Generate and copy your Preswald API key
    Deploy your app using the following command:

    preswald deploy --target structured --github --api-key hello.py

    Replace <your-github-username> and <structured-api-key> with your credentials.

3. Verify the deployment

    Once deployment is complete, a live preview link will be provided.
    Open the link in your browser and verify that your app is running.