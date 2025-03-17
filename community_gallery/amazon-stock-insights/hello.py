from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff  # for the correlation heatmap

# Dashboard Title
text("# Amazon Stock Data Dashboard")
text("Explore Amazon stock data (2000-2025).")

# Load Data
connect()
df = get_df('amazon')
df['date'] = pd.to_datetime(df['date'])


#  Scatter Plot: Volume vs. Close
fig_scatter = px.scatter(
    df,
    x='volume',
    y='close',
    title='Volume vs. Closing Price',
    labels={'volume': 'Volume', 'close': 'Close Price (USD)'},
    template='plotly_white'
)
plotly(fig_scatter)

# Distribution of Daily Returns
df['daily_return'] = df['close'].pct_change()
fig_returns = px.histogram(
    df.dropna(subset=['daily_return']),  # remove rows with NaN in daily_return
    x='daily_return',
    nbins=50,
    title='Distribution of Daily Returns',
    labels={'daily_return': 'Daily Return'},
    template='plotly_white'
)
plotly(fig_returns)

#  Correlation Heatmap
numeric_cols = ['open', 'high', 'low', 'close', 'adj_close', 'volume']
corr_matrix = df[numeric_cols].corr()

fig_corr = ff.create_annotated_heatmap(
    z=corr_matrix.values,
    x=corr_matrix.columns.tolist(),
    y=corr_matrix.columns.tolist(),
    colorscale='Viridis',
    showscale=True
)
fig_corr.update_layout(title='Correlation Matrix', template='plotly_white')
plotly(fig_corr)

# Table Preview
text("## Data Preview")
table(df.head(10))
