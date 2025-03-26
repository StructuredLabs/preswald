from preswald import text, plotly, connect, get_df, table
import plotly.express as px

text("# Credit Card Fraud Analysis")
text("Visualizing fraud transaction trends.")

# Load the CSV
target_source = 'fraud_data_csv'  # Ensure this matches your data source name
connect()  # Load in all sources

df = get_df('fraud_data_csv')
#available_sources = list_sources()
#text(f"Available sources: {available_sources}")
#df = get_df(target_source)

# Create a bar plot for fraud vs. non-fraud transactions
fraud_counts = df['is_fraud'].value_counts().reset_index()
fraud_counts.columns = ['Fraud Status', 'Count']
fraud_counts['Fraud Status'] = fraud_counts['Fraud Status'].map({0: 'Non-Fraud', 1: 'Fraud'})

fig = px.bar(fraud_counts, x='Fraud Status', y='Count',
             title='Fraud vs. Non-Fraud Transactions',
             labels={'Count': 'Number of Transactions', 'Fraud Status': 'Transaction Type'},
             color='Fraud Status',
             text='Count')

fig.update_traces(textposition='outside')
fig.update_layout(template='plotly_white')

# Show the plot
plotly(fig)

# Create a histogram for transaction amounts
fig2 = px.histogram(df, x='amt', nbins=50, title='Transaction Amount Distribution',
                    labels={'amt': 'Transaction Amount ($)'}, color='is_fraud',
                    color_discrete_map={0: 'blue', 1: 'red'})

fig2.update_layout(template='plotly_white')

# Show the second plot
plotly(fig2)

# Show the data
table(df.head())
