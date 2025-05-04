from preswald import text, plotly, connect, get_df, table, query,slider
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

text("NVIDIA Stock Price Analysis")


connect() 
df = get_df('NVIDIA_csv')
print(df.head())

df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
threshold = slider("Volume Threshold", min_val=100000000, max_val=10000000000, default=50)
fig=go.Figure()
fig.add_trace(go.Scatter(x=df['Date'][df["Volume"] > threshold], y=df['Close'][df["Volume"] > threshold], mode='lines', name='Close', line=dict(color='blue')))

sql = "SELECT * FROM NVIDIA_csv WHERE ATR >= 0.001"
filtered_df = query(sql, "NVIDIA_csv")
filtered_df['Date'] = filtered_df['Date'].dt.strftime('%Y-%m-%d')
fig.add_scatter(x=filtered_df['Date'][filtered_df["Volume"] > threshold], y=filtered_df['High'][filtered_df["Volume"] > threshold], mode='lines', name='High', line=dict(color='green'))
fig.add_scatter(x=filtered_df['Date'][filtered_df["Volume"] > threshold], y=filtered_df['Low'][filtered_df["Volume"] > threshold], mode='lines', name='Low', line=dict(color='red'))



fig.update_traces(textposition='top center', marker=dict(size=6, color='red'))


fig.update_layout(template='plotly_white')


plotly(fig)


table(df[df["Volume"] > threshold], title="Dynamic Data View")