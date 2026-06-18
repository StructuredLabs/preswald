from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px

text("# Sleep Health and Lifestyle Dashboard")
text("This dashboard will help you understand the relationship between sleep and lifestyle factors based on gender, BMI category and sleep disorders.")

# Load the CSV
connect()
df = get_df('sleep_health')

#Overview of the data
total_participants = len(df)
male_participants = len(df[df['Gender'] == 'Male'])
female_participants = len(df[df['Gender'] == 'Female'])
disorder_count = len(df[df['Sleep Disorder'] != 'None'])

#Display of summary statistics
text("## Sleep Health at a Glance")
text(f"**Total Participants:** {total_participants} | **Males:** {male_participants} | **Females:** {female_participants} | **Suffering from Sleep Disorders:** {disorder_count}")

#Sleep Duration Breakdown
min_sleep = float(df['Sleep Duration'].min())
avg_sleep = float(df['Sleep Duration'].mean())
max_sleep = float(df['Sleep Duration'].max())

#Filtering data based on sleep duration
text("## Filter by Sleep Duration")
sleep_threshold = slider("Minimum Sleep Duration (hours)", 
                        min_val=min_sleep, 
                        max_val=max_sleep, 
                        default=min_sleep)

# Filter data based on slider value
filtered_df = df[df['Sleep Duration'] >= sleep_threshold]
text(f"Showing {len(filtered_df)} records with Sleep Duration ≥ {sleep_threshold:.2f} hours")

#Gender vs BMI Category
bmi_by_gender = filtered_df.groupby(['Gender', 'BMI Category']).size().reset_index(name='Count')
fig1 = px.bar(
    bmi_by_gender,
    x = 'Gender',
    y = 'Count',
    color = 'BMI Category',
    title = 'BMI Category by Gender',
    labels = {'Count': 'Number of People', 'BMI Category': 'BMI Category Type'},
    barmode = 'group'
)

#Display the graph
plotly(fig1)

#Gender vs Sleep Disorders
disorder_by_gender = filtered_df.groupby(['Gender', 'Sleep Disorder']).size().reset_index(name='Count')
fig2 = px.bar(
    disorder_by_gender, 
    x='Gender', 
    y='Count', 
    color='Sleep Disorder',
    title='Sleep Disorders by Gender',
    labels={'Count': 'Number of People', 'Sleep Disorder': 'Sleep Disorder Type'},
    barmode='group'
)

#Display the graph
plotly(fig2)

#Dataset as table
text("## Dataset overview")
table(filtered_df.head(100), title="Sleep Health and Lifestyle Dataset")
