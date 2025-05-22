import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from preswald import connect, get_df, plotly, table, text
import numpy as np

# Report Title
text("# Customer Churn Analysis")
text(
    "This report analyzes customer churn for a telecom company, exploring factors like demographics, services, contract type, and billing that contribute to churn."
)

# Load the CSV
connect()
df = pd.read_csv("data/customer_churn.csv")

df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df["TotalCharges"].fillna(0, inplace=True)
df["Churn"] = df["Churn"].replace({"No": 0, "Yes": 1})  # Encode Churn

# 1. Churn Rate across Different Services
text("## Churn Rate by Services")
services = ["PhoneService", "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
for service in services:
    fig = px.histogram(df, x=service, color="Churn", barmode="group", title=f"Churn Rate by {service}").update_layout(template="plotly_white")
    plotly(fig)


# 2. Churn Rate by Payment Method
text("## Churn Rate by Payment Method")
fig_payment = px.histogram(df, x="PaymentMethod", color="Churn", barmode="group", title="Churn by Payment Method").update_layout(template="plotly_white")
plotly(fig_payment)


# 3. Churn Rate vs. Tenure (Scatter without statsmodels trendline)
text("## Churn vs Tenure")

# Calculate average churn rate by tenure using pandas
tenure_churn = df.groupby('tenure')['Churn'].mean().reset_index()
tenure_churn['ChurnRate'] = tenure_churn['Churn'] * 100  # Convert to percentage

# Create scatter plot with custom line
fig_tenure = px.scatter(tenure_churn, x="tenure", y="ChurnRate", 
                       title="Average Churn Rate by Tenure")

# Add a smoothed line using moving average from pandas
window = 5  # Adjust window size as needed
if len(tenure_churn) >= window:
    tenure_churn['SmoothedChurnRate'] = tenure_churn['ChurnRate'].rolling(window=window, center=True).mean()
    fig_tenure.add_trace(go.Scatter(x=tenure_churn['tenure'], y=tenure_churn['SmoothedChurnRate'],
                                  mode='lines', name='Trend (Moving Avg)'))

fig_tenure.update_layout(template="plotly_white", 
                       xaxis_title="Tenure (months)",
                       yaxis_title="Churn Rate (%)")
plotly(fig_tenure)


# 4. Distribution of Total Charges (Histogram, Colored by Churn)
text("## Total Charges Distribution (Colored by Churn)")
fig_charges = px.histogram(df, x="TotalCharges", color="Churn", title="Distribution of Total Charges", nbins=50,  # Adjust bins as needed
                         marginal="box").update_layout(template="plotly_white") # Boxplot on the margin
plotly(fig_charges)

# 5. Churn Rate by Number of Dependents
text("## Churn by Dependents")
fig_dependents = px.histogram(df, x="Dependents", color="Churn", title="Churn Rate by Number of Dependents", barmode='group').update_layout(template="plotly_white")
plotly(fig_dependents)


# 6. Correlation Heatmap
text("## Feature Correlations")
numeric_df = df.select_dtypes(include=np.number) # select only numeric
corr_matrix = numeric_df.corr()
fig_corr = px.imshow(corr_matrix, title="Feature Correlation Heatmap",
                    color_continuous_scale="RdBu_r",  # Red-Blue color scale
                    zmin=-1, zmax=1).update_layout(template="plotly_white")
plotly(fig_corr)

# 7. Add Contract Type Analysis (additional insight)
text("## Churn by Contract Type")
fig_contract = px.histogram(df, x="Contract", color="Churn", 
                           title="Churn by Contract Type", 
                           barmode='group').update_layout(template="plotly_white")
plotly(fig_contract)

# 8. Monthly Charges vs Total Charges colored by churn
text("## Monthly vs Total Charges")
fig_charges_comp = px.scatter(df, x="MonthlyCharges", y="TotalCharges", 
                             color="Churn", opacity=0.7,
                             title="Monthly vs Total Charges",
                             color_discrete_sequence=["blue", "red"])
fig_charges_comp.update_layout(template="plotly_white")
plotly(fig_charges_comp)

# Show the data
text("## Sample Data")
table(df, limit=10) # Still showing a subset