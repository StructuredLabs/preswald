import pandas as pd
import plotly.express as px
from preswald import text, plotly, connect, get_df, table, query, slider, selectbox
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

text("# Welcome to Titanic Survival Analysis!")
text("Explore how different factors influenced survival rates. 🚢")

connect()
df = get_df('sample_csv')

text("# Initial Data View")
table(df.head(), title="First Few Rows of Data")

slider_age = slider("Age Threshold", min_val=0, max_val=df['Age'].max(), default=20)
slider_fare = slider("Fare Threshold", min_val=0, max_val=df['Fare'].max(), default=50)

filtered_df = df[(df["Age"] > slider_age) & (df["Fare"] > slider_fare)]

text("# Dynamic Data View Based on Age and Fare")
fig = px.scatter(filtered_df, x="Age", y="Fare", color="Survived")
fig.update_layout(xaxis=dict(title="Age (years)"), yaxis=dict(title="Fare ($)"))
plotly(fig)

table(filtered_df, title="Filtered Data")

df['AgeGroup'] = pd.cut(df['Age'], bins=[0, 12, 18, 35, 60, 100], labels=['Child', 'Teen', 'Young Adult', 'Adult', 'Senior'])

gender = selectbox("Select Gender", options=["All", "Male", "Female"], default="All")
pclass = selectbox("Select Class", options=["All", 1, 2, 3], default="All")

filtered_df = df.copy()
if gender != "All":
    filtered_df = filtered_df[filtered_df['Sex'] == gender.lower()]
if pclass != "All":
    filtered_df = filtered_df[filtered_df['Pclass'] == pclass]

text("## Survival Analysis Dashboard")

fig = make_subplots(rows=2, cols=1, specs=[[{"type": "pie"}], [{"type": "box"}]], 
                   subplot_titles=("Survival Distribution", "Fare Distribution by Class"))

survival_counts = filtered_df['Survived'].value_counts()
fig.add_trace(go.Pie(labels=['Died', 'Survived'], values=survival_counts.values, 
                    marker_colors=['#FF6B6B', '#4ECDC4']), row=1, col=1)

survival_by_age = filtered_df.groupby('AgeGroup')['Survived'].mean().reset_index()

fig.add_trace(go.Box(x=filtered_df['Pclass'], y=filtered_df['Fare'], marker_color='#FF9F1C'), row=2, col=1)

fig.update_layout(height=800, showlegend=False, template='plotly_white')
plotly(fig)

text("## Summary Statistics")
table(filtered_df.describe(), title="Statistical Summary")

df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
df_clean = df.dropna(subset=['Age', 'Fare', 'FamilySize'])

point_size = slider("Point Size", min_val=3, max_val=10, default=5)
opacity = slider("Opacity", min_val=0.1, max_val=1.0, default=0.7, step=0.1)

fig = go.Figure(data=[go.Scatter3d(
    x=df_clean['Age'], y=df_clean['Fare'], z=df_clean['FamilySize'], mode='markers',
    marker=dict(size=point_size, color=df_clean['Survived'], colorscale='Viridis', 
               opacity=opacity, colorbar=dict(title="Survived")),
    text=df_clean['Name'],
    hovertemplate="<b>%{text}</b><br>Age: %{x:.1f}<br>Fare: $%{y:.2f}<br>Family Size: %{z}<br><extra></extra>")])

fig.update_layout(
    title='3D Visualization of Survival Factors',
    scene=dict(xaxis_title='Age', yaxis_title='Fare', zaxis_title='Family Size',
              camera=dict(up=dict(x=0, y=0, z=1), center=dict(x=0, y=0, z=0), eye=dict(x=1.5, y=1.5, z=1.5))),
    margin=dict(l=0, r=0, b=0, t=30), template='plotly_dark')

plotly(fig)

text("## Insights from 3D Visualization")
text("""
- The 3D visualization reveals clusters of survival that might not be apparent in 2D plots
- Notice how family size interacts with age and fare to influence survival probability
- Older passengers with lower fares and high family sizes appear to have lower survival rates
""")

df['AgeGroup'] = pd.cut(df['Age'].fillna(df['Age'].median()), 
                       bins=[0, 12, 18, 35, 60, 100], 
                       labels=['Child', 'Teen', 'Young Adult', 'Adult', 'Senior'])
df['FareGroup'] = pd.qcut(df['Fare'].fillna(df['Fare'].median()), 
                         q=4, labels=['Low', 'Medium-Low', 'Medium-High', 'High'])

pclass_labels = [f"Class {i}" for i in range(1, 4)]
gender_labels = ["Male", "Female"]
age_labels = ['Child', 'Teen', 'Young Adult', 'Adult', 'Senior']
fare_labels = ['Low', 'Medium-Low', 'Medium-High', 'High']
outcome_labels = ["Died", "Survived"]

all_nodes = pclass_labels + gender_labels + age_labels + fare_labels + outcome_labels
node_indices = {node: i for i, node in enumerate(all_nodes)}

links_source, links_target, links_value = [], [], []

for pclass in range(1, 4):
    for gender in ["male", "female"]:
        count = len(df[(df['Pclass'] == pclass) & (df['Sex'] == gender)])
        if count > 0:
            links_source.append(node_indices[f"Class {pclass}"])
            links_target.append(node_indices["Male" if gender == "male" else "Female"])
            links_value.append(count)

for gender in ["male", "female"]:
    for age_group in age_labels:
        count = len(df[(df['Sex'] == gender) & (df['AgeGroup'] == age_group)])
        if count > 0:
            links_source.append(node_indices["Male" if gender == "male" else "Female"])
            links_target.append(node_indices[age_group])
            links_value.append(count)

for age_group in age_labels:
    for fare_group in fare_labels:
        count = len(df[(df['AgeGroup'] == age_group) & (df['FareGroup'] == fare_group)])
        if count > 0:
            links_source.append(node_indices[age_group])
            links_target.append(node_indices[fare_group])
            links_value.append(count)

for fare_group in fare_labels:
    for survived in [0, 1]:
        count = len(df[(df['FareGroup'] == fare_group) & (df['Survived'] == survived)])
        if count > 0:
            links_source.append(node_indices[fare_group])
            links_target.append(node_indices["Survived" if survived == 1 else "Died"])
            links_value.append(count)

fig = go.Figure(data=[go.Sankey(
    node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=all_nodes,
             color=["#1f77b4"] * 3 + ["#ff7f0e"] * 2 + ["#2ca02c"] * 5 + ["#d62728"] * 4 + ["#9467bd"] * 2),
    link=dict(source=links_source, target=links_target, value=links_value,
             color=["rgba(0,0,255,0.2)"] * len(links_source)))])

fig.update_layout(title_text="Passenger Flow Through Categories to Survival Outcome", font_size=12, height=800)
plotly(fig)

text("## Insights from the Sankey Diagram")
text("""
- The Sankey diagram visualizes how passengers flowed through different categories to their ultimate survival outcome
- Notice the thickness of flows between categories, indicating the volume of passengers in each path
- This helps identify which combinations of factors were most associated with survival or death
- For example, you can trace the path from Class 1 → Female → Adult → High Fare → Survived to see a common survival pattern
""")

df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
df['IsAlone'] = (df['FamilySize'] == 1).astype(int)
df['Title'] = df['Name'].str.extract(' ([A-Za-z]+)\.', expand=False)
title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Dr": 5, "Rev": 6, "Other": 7}
df['Title'] = df['Title'].map(lambda x: title_mapping.get(x, 7))
df['Sex'] = df['Sex'].map({"male": 0, "female": 1})

df['Age'].fillna(df['Age'].median(), inplace=True)
df['Fare'].fillna(df['Fare'].median(), inplace=True)
df['Embarked'].fillna('S', inplace=True)
df['Embarked'] = df['Embarked'].map({"S": 0, "C": 1, "Q": 2})

features = ['Survived', 'Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 
           'Fare', 'Embarked', 'FamilySize', 'IsAlone', 'Title']

correlation_method = selectbox("Correlation Method", options=["pearson", "spearman", "kendall"], default="pearson")
sort_by = selectbox("Sort By", options=["None", "Survived"], default="None")

corr_matrix = df[features].corr(method=correlation_method)

if sort_by == "Survived":
    survived_corr = corr_matrix['Survived'].drop('Survived')
    sorted_features = ['Survived'] + list(survived_corr.abs().sort_values(ascending=False).index)
    corr_matrix = corr_matrix.reindex(sorted_features)[sorted_features]

fig = go.Figure(data=go.Heatmap(
    z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.index, colorscale='RdBu_r',
    zmin=-1, zmax=1, text=np.round(corr_matrix.values, 2),
    hovertemplate='%{y} & %{x}<br>Correlation: %{z:.2f}<extra></extra>', texttemplate='%{text:.2f}'))

fig.update_layout(
    title=f'Correlation Heatmap ({correlation_method} method)',
    height=700, width=700, xaxis_showgrid=False, yaxis_showgrid=False, yaxis_autorange='reversed')

plotly(fig)

text("## Feature Correlation with Survival")
survival_corr = corr_matrix['Survived'].drop('Survived').sort_values(ascending=False)
survival_corr_df = pd.DataFrame({
    'Feature': survival_corr.index,
    'Correlation with Survival': survival_corr.values
})
table(survival_corr_df, title="Features Ranked by Correlation with Survival")

text("## Insights from Correlation Analysis")
text("""
- Sex has the strongest correlation with survival, indicating women were more likely to survive
- Higher class (lower Pclass value) correlates with higher survival rates
- Title (extracted from name) shows significant correlation, reflecting social status
""")
# prswld-cb92bbd3-0c09-4e82-b35c-59b02be8bd5a
