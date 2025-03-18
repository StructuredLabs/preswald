from preswald.interfaces.components import text, plotly, table
from preswald.interfaces.data import connect, get_df
import pandas as pd
import plotly.express as px

text("# API Integration Test")
text("Testing the Preswald API source  ")

# Connect to load all data sources
connect()

# Get data from the API
text("## API Data")
text("Fetching data from JSONPlaceholder API...")
df_api = get_df('jsonplaceholder_api')
table(df_api.head(10), title="Posts from JSONPlaceholder API")

text("## API Data Statistics")
stats = pd.DataFrame({
    'Column': df_api.columns,
    'Data Type': df_api.dtypes.astype(str),
    'Non-Null Count': df_api.count(),
    'Unique Values': [df_api[col].nunique() for col in df_api.columns]
})
table(stats, title="API Data Statistics")

text("## API Data Visualization")
if 'userId' in df_api.columns and 'id' in df_api.columns:
    user_post_counts = df_api['userId'].value_counts().reset_index()
    user_post_counts.columns = ['userId', 'post_count']
    
    fig = px.bar(
        user_post_counts,
        x='userId', 
        y='post_count',
        title='Post Count by User ID',
        labels={'userId': 'User ID', 'post_count': 'Number of Posts'}
    )
    fig.update_layout(template='plotly_white')
    plotly(fig)
