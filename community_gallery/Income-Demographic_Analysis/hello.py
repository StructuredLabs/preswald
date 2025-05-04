from preswald import connect, get_df, query, text, table, slider, plotly, checkbox
import plotly.express as px
import pandas as pd
import requests
from io import StringIO
# zconnectto data sources
connect()

# Load the income dataset
def load_data():
    url = "https://raw.githubusercontent.com/Waleedprw22/income_dataset/refs/heads/main/Adult_data.csv"
    response = requests.get(url)
    return pd.read_csv(StringIO(response.text))

# Load the income dataset
df = load_data()


# Style the Header UI
text("# 📊 Census Demographic Analysis")
text("### Explore how different demographic factors influence income levels")
text("---")

# Create a section for filters
text("## 🔍 Filter Options")

# Create columns for filters (visual organization)
text("### Age Range")
min_age = slider("Minimum Age", min_val=16, max_val=90, default=25)
max_age = slider("Maximum Age", min_val=16, max_val=90, default=65)

text("### 🎓 Education Level")
text("Select which education levels to include in the analysis:")
show_all_education = checkbox("Show All Education Levels", default=True)

# Categorize educational groups for a cleaner look
text("**Academic Degrees**")
show_bachelors = checkbox("Bachelors", default=True)
show_masters = checkbox("Masters", default=True)
show_doctorate = checkbox("Doctorate", default=True)
text("**High School & College**")
show_hs = checkbox("High School Graduate", default=True)
show_some_college = checkbox("Some College", default=True)

# Establish filters for gender based searches.
text("### 👫 Gender")
show_male = checkbox("Male", default=True)
show_female = checkbox("Female", default=True)

# Filter based on work hours
text("### ⏱️ Work Hours")
min_hours = slider("Minimum Work Hours per Week", min_val=1, max_val=100, default=35)

# Filter based on income range
text("### 💰 Income Range")
show_high_income = checkbox("Show >50K Income", default=True)
show_low_income = checkbox("Show ≤50K Income", default=True)

text("---")

# Filter data based on user input
filtered_df = df[(df["age"] >= min_age) & (df["age"] <= max_age) &
                (df["hours-per-week"] >= min_hours)]

# Apply education filter
if not show_all_education:
    education_filters = []
    if show_hs:
        education_filters.append("HS-grad")
    if show_some_college:
        education_filters.append("Some-college")
    if show_bachelors:
        education_filters.append("Bachelors")
    if show_masters:
        education_filters.append("Masters")
    if show_doctorate:
        education_filters.append("Doctorate")
    
    # Only apply filter if at least one option is selected
    if education_filters:
        filtered_df = filtered_df[filtered_df["education"].isin(education_filters)]

# Apply gender filter
gender_filters = []
if show_male:
    gender_filters.append("Male")
if show_female:
    gender_filters.append("Female")
# Only apply filter if at least one option is selected
if gender_filters:
    filtered_df = filtered_df[filtered_df["sex"].isin(gender_filters)]

# Apply income class filters
income_filters = []
if show_high_income:
    income_filters.append(">50K")
if show_low_income:
    income_filters.append("<=50K")
filtered_df = filtered_df[filtered_df["class"].isin(income_filters)]

# Add a dataset summary
text("## 📋 Dataset Overview")
text(f"**Current Selection:** {len(filtered_df)} records")
text(f"**Income Distribution:** {(filtered_df['class'] == '>50K').sum()} earning >$50K ({(filtered_df['class'] == '>50K').mean()*100:.1f}%) | {(filtered_df['class'] == '<=50K').sum()} earning ≤$50K ({(filtered_df['class'] == '<=50K').mean()*100:.1f}%)")

# Display the filtered data with better styling
text("### Sample Records")
table(filtered_df.head(10), title="Census Data Sample")

# Create visualizations with improved styling
text("## 📈 Visualizations")

# Use a more pleasing color palette
color_map = {">50K": "#2E8B57", "<=50K": "#CD5C5C"}  # Sea Green and Indian Red

text("### Age Distribution by Income Class")
fig1 = px.histogram(filtered_df, x="age", color="class",
                   title="Age Distribution by Income Class",
                   barmode="overlay", opacity=0.7,
                   color_discrete_map=color_map)
fig1.update_layout(
    plot_bgcolor='white',
    xaxis_title="Age",
    yaxis_title="Count",
    legend_title="Income Level"
)
plotly(fig1)

text("### Hours Worked vs. Age")
fig2 = px.scatter(filtered_df, x="age", y="hours-per-week", color="class",
                 title="Hours Worked vs. Age by Income Class",
                 color_discrete_map=color_map)

fig2.update_layout(
    plot_bgcolor='white',
    xaxis_title="Age",
    yaxis_title="Hours per Week",
    legend_title="Income Level"
)
plotly(fig2)

text("### Income Distribution by Education Level")
education_income = filtered_df.groupby(["education", "class"]).size().reset_index(name="count")
fig3 = px.bar(education_income, x="education", y="count", color="class",
             title="Income Distribution by Education Level",
             color_discrete_map=color_map)
fig3.update_layout(
    plot_bgcolor='white',
    xaxis_title="Education Level",
    yaxis_title="Count",
    legend_title="Income Level"
)
# Sort bars by education level
fig3.update_xaxes(categoryorder='category ascending')
plotly(fig3)

text("### Occupation Distribution")
occupation_counts = filtered_df["occupation"].value_counts().reset_index()
occupation_counts.columns = ["occupation", "count"]
fig4 = px.pie(occupation_counts, values="count", names="occupation",
             title="Distribution by Occupation")
fig4.update_traces(textposition='inside', textinfo='percent+label')
fig4.update_layout(
    plot_bgcolor='white'
)
plotly(fig4)

# Calculate some summary statistics with better formatting
text("## 📊 Summary Statistics")

# Create a more visually appealing summary
high_income_pct = (filtered_df["class"] == ">50K").mean() * 100
avg_age_high = filtered_df[filtered_df["class"] == ">50K"]["age"].mean()
avg_age_low = filtered_df[filtered_df["class"] == "<=50K"]["age"].mean()
avg_hours_high = filtered_df[filtered_df["class"] == ">50K"]["hours-per-week"].mean()
avg_hours_low = filtered_df[filtered_df["class"] == "<=50K"]["hours-per-week"].mean()

# High income stats
text("### 💸 High Income Group (>$50K)")
text(f"- **Average age:** {avg_age_high:.1f} years")
text(f"- **Average weekly hours:** {avg_hours_high:.1f} hours")

# Low income stats
text("### 💰 Lower Income Group (≤$50K)")
text(f"- **Average age:** {avg_age_low:.1f} years")
text(f"- **Average weekly hours:** {avg_hours_low:.1f} hours")

# Additional interesting statistics
text("### 🔍 Additional Insights")

# Education distribution
top_education_high = "No data available" # Default
top_education_low = "No data available" # Default

# Error-safe way to get top education levels
try:
    high_income_df = filtered_df[filtered_df["class"] == ">50K"]
    if not high_income_df.empty:
        top_education_high = high_income_df["education"].value_counts().index[0]
        text(f"- **Most common education (>$50K):** {top_education_high}")
    else:
        text("- **Most common education (>$50K):** No data available")
except:
    text("- **Most common education (>$50K):** No data available")

try:
    low_income_df = filtered_df[filtered_df["class"] == "<=50K"]
    if not low_income_df.empty:
        top_education_low = low_income_df["education"].value_counts().index[0]
        text(f"- **Most common education (≤$50K):** {top_education_low}")
    else:
        text("- **Most common education (≤$50K):** No data available")
except:
    text("- **Most common education (≤$50K):** No data available")


text(f"- **Most common education (>$50K):** {top_education_high}")
text(f"- **Most common education (≤$50K):** {top_education_low}")

# Footer
text("---")
text("*Dashboard created with Preswald and Plotly*")
