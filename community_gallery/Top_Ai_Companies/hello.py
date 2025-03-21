import pandas as pd
import numpy as np
import plotly.express as px
from preswald import connect, get_df, text, table, plotly
connect()
text("##  **Top AI Companies Dashboard** 🌎")
df = get_df("Ai_companies_csv")


df.columns = ["Company", "Description", "Headquarters", "Founded", "Revenue", "Glassdoor Score"]
#data Processing and Cleaning

def convert_revenue(value):
    if isinstance(value, str):
        value = value.replace("$", "").replace(",", "").lower()
        if "billion" in value:
            return float(value.replace("billion", "").strip()) * 1e9
        elif "million" in value:
            return float(value.replace("million", "").strip()) * 1e6
    return pd.NA

df["Revenue"] = df["Revenue"].replace(["N/A", "None", ""], pd.NA).apply(convert_revenue)
df["Glassdoor Score"] = df["Glassdoor Score"].replace(["N/A", "None", ""], pd.NA)
df["Glassdoor Score"] = df["Glassdoor Score"].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
df["Glassdoor Score"] = df["Glassdoor Score"].replace(5.0, 4.5)  
df["Log Revenue"] = np.log1p(df["Revenue"])
df["Country"] = df["Headquarters"].apply(lambda x: x.split(",")[-1].strip())


table(title='Processed Dataset Rows', data=df.head())

#Bar Graph to Represent top 5 AI Companies
top_revenue = df.nlargest(5, "Revenue")
fig1 = px.bar(top_revenue, x="Company", y="Revenue", text="Revenue",  color="Revenue")
fig1.update_layout(
    title=dict(
        text="Top 5 AI Companies by Revenue",
        x=0.5,
        font=dict(size=42, family="Arial", color="black", weight="bold")
    ),template='plotly_white'
    )
plotly(fig1)


#Line Graph to represent Growth of AI Companies Over Years
df["Founded"] = pd.to_numeric(df["Founded"], errors="coerce")  
founded_count = df["Founded"].dropna().astype(int).value_counts().reset_index()
founded_count.columns = ["Year", "Company Count"]
fig2 = px.line(founded_count.sort_values("Year"), x="Year", y="Company Count", markers=True)
fig2.update_layout(title=dict(
        text="Number of AI Companies Founded Over Time",
        x=0.5,
        font=dict(size=42, family="Arial", color="black", weight="bold")
    ))
plotly(fig2)

#Geographical Distribution of AI Companies
df["Country"] = df["Headquarters"].apply(lambda x: x.split(",")[-1].strip())
location_count = df["Country"].value_counts().reset_index()
location_count.columns = ["Country", "Company Count"]
fig3 = px.choropleth(location_count, locations="Country", locationmode="country names",
                     color="Company Count")
fig3.update_layout(title=dict(
        text="AI Companies by Country",
        x=0.5,
        font=dict(size=42, family="Arial", color="black", weight="bold")
    ))
plotly(fig3)


#Distribution of Company Revenues
fig4 = px.histogram(df, x="Revenue", nbins=30,
                    color_discrete_sequence=["green"])
fig4.update_layout(title=dict(
        text="Distribution of Company Revenues",
        x=0.5,
        font=dict(size=42, family="Arial", color="black", weight="bold")
    ))
plotly(fig4)


# Correlation Heatmap
corr_matrix = df[["Founded", "Log Revenue", "Glassdoor Score"]].corr()
fig5 = px.imshow(
    corr_matrix,
    x=corr_matrix.columns,
    y=corr_matrix.columns,
    color_continuous_scale="Greens",
    text_auto=True,
    zmin=-0.5,
    zmax=1.0
)
fig5.update_layout(
    title=dict(
        text="Correlation Heatmap",
        x=0.5,
        font=dict(size=42, family="Arial", color="black", weight="bold")
    ),
    template="plotly_white",
)
plotly(fig5)


fig6 = px.scatter(
    df.dropna(subset=["Glassdoor Score", "Log Revenue"]),
    x="Glassdoor Score",
    y="Log Revenue",
    color_discrete_sequence=["green"],
    hover_data=["Company"]  
)
fig6.update_layout(
    title=dict(
        text="Glassdoor Score vs Log of Annual Revenue",
        x=0.5,
        font=dict(size=42, family="Arial", color="black", weight="bold")
    ),
    template="plotly_white",
    xaxis=dict(range=[2.9, 5.0]),  
    yaxis=dict(range=[-0.5, 6.5])  
)

plotly(fig6)


# Bubble chart for AI Companies: Revenue vs Glassdoor Score by Industry 
def extract_category(description):
    if "security" in description.lower() or "cyber" in description.lower() or "threat" in description.lower():
        return "Cybersecurity"
    elif "robot" in description.lower() or "drone" in description.lower():
        return "Robotics"
    elif "healthcare" in description.lower() or "medical" in description.lower() or "drug" in description.lower():
        return "Healthcare"
    elif "education" in description.lower() or "learning" in description.lower():
        return "Education"
    elif "finance" in description.lower() or "bank" in description.lower() or "credit" in description.lower():
        return "Finance"
    elif "data" in description.lower() or "analytics" in description.lower():
        return "Data Analytics"
    else:
        return "Other"

df["Category"] = df["Description"].apply(extract_category)


fig7 = px.scatter(
    df.dropna(subset=["Revenue", "Glassdoor Score"]),
    x="Glassdoor Score",
    y="Revenue",
    color="Category",
    size="Log Revenue",  
    hover_name="Company",
    hover_data=["Revenue", "Log Revenue", "Category"],
    size_max=25,
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig7.update_layout(
    template="plotly_white",
    xaxis_range=[2.8, 5.0],
    xaxis_title="Glassdoor Score",
    yaxis_title="Revenue",
    legend_title="Category",
    height=600,
    width=900,
     title=dict(
        text="AI Companies: Revenue vs Glassdoor Score by Industry Category",
        x=0.5,
        font=dict(size=42, family="Arial", color="black", weight="bold")
    )
)

fig7.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
fig7.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

plotly(fig7)