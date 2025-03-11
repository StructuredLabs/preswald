import pandas as pd
import plotly.express as px
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
services = ["PhoneService", "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
for service in services:
    fig = px.histogram(df, x=service, color="Churn", barmode="group", title=f"Churn Rate by {service}").update_layout(template="plotly_white")
    plotly(fig)


# 2. Churn Rate by Payment Method
text("## Churn Rate by Payment Method")
fig_payment = px.histogram(df, x="PaymentMethod", color="Churn", barmode="group", title="Churn by Payment Method").update_layout(template="plotly_white")
plotly(fig_payment)


# 3. Churn Rate vs. Tenure (Scatter with Trendline)
text("## Churn vs Tenure")
fig_tenure = px.scatter(
    df, x="tenure", y="Churn", trendline="ols", title="Churn vs. Tenure"
).update_layout(template="plotly_white")
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
fig_corr = px.imshow(corr_matrix, title="Feature Correlation Heatmap").update_layout(template="plotly_white")
plotly(fig_corr)



# Show the data
table(df, limit=10) # Still showing a subset