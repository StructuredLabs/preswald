import pandas as pd
from preswald import connect, get_df, table, text, slider, plotly
import plotly.express as px

# Initialize connection to Preswald
connect()

# Load Titanic dataset (assuming columns are already named correctly)
df = pd.read_csv("data/titanic.csv", usecols=lambda col: col not in ["Cabin", "Ticket", "Name"])
df.dropna(inplace=True)  # Remove missing values

# App UI
text("# Titanic Data Exploration")
text("### Filter passengers by age")

# Age filter
age_filter = slider("Select Age", min_val=int(df["Age"].min()), max_val=int(df["Age"].max()), default=30)

# Display filtered data
filtered_df = df[df["Age"] <= age_filter]
table(filtered_df, title="Passengers Below Selected Age")

# Visualization
text("### Survival Rate Based on Passenger Class")

fig = px.bar(df, x="Pclass", y="Survived", color="Sex", barmode="group",
             title="Survival Rate by Class and Gender")
plotly(fig)
