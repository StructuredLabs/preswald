from preswald import connect, get_df, text, table, slider, plotly
import plotly.express as px
import pandas as pd

# Try Preswald connection
try:
    connect()
    df = get_df("finance")
    if df is None:
        raise ValueError("get_df returned None")
except Exception as e:
    print(f"Preswald connection failed: {e}")
    # Fallback: Load CSV directly
    df = pd.read_csv("data/finance_data.csv")

# Clean column names (remove spaces)
df.columns = [col.replace(' ', '_') for col in df.columns]

print(f"Original df shape: {df.shape}")
print(f"df columns: {df.columns}")
print(f"df head:\n{df.head()}")

# Title of the app
text("# Finance Investment Analysis")

# Add a slider for age threshold
min_age = int(df['age'].min())
max_age = int(df['age'].max())
threshold = slider("Minimum Age", min_val=min_age, max_val=max_age, default=min_age)

# Filter data dynamically based on slider
filtered_df = df[df['age'] >= threshold]
print(f"Filtered df shape: {filtered_df.shape}")
print(f"Filtered df head:\n{filtered_df.head()}")

# Display filtered data in a table
table(filtered_df[["gender", "age", "Avenue", "What_are_your_savings_objectives?"]], title="Investors Above Age Threshold")

# Scatter plot: Age vs Mutual Funds, colored by gender
fig1 = px.scatter(filtered_df, x="age", y="Mutual_Funds", color="gender", 
                  title="Age vs Mutual Funds Investment by Gender",
                  labels={"age": "Age", "Mutual_Funds": "Mutual Funds Score"},
                  hover_data=["Avenue", "What_are_your_savings_objectives?"])
plotly(fig1)

# Bar plot: Average investment scores by gender
investment_columns = ["Mutual_Funds", "Equity_Market", "Debentures", "Government_Bonds", "Fixed_Deposits", "PPF", "Gold"]
avg_scores = filtered_df.groupby("gender")[investment_columns].mean().reset_index()
avg_scores_melted = avg_scores.melt(id_vars="gender", value_vars=investment_columns, 
                                     var_name="Investment_Avenue", value_name="Average_Score")
fig2 = px.bar(avg_scores_melted, x="Investment_Avenue", y="Average_Score", color="gender", barmode="group",
              title="Average Investment Scores by Gender",
              labels={"Investment_Avenue": "Investment Avenue", "Average_Score": "Average Score"})
plotly(fig2)
