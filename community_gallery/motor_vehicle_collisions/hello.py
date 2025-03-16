from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# App title and description
text("# Motor Vehicle Collisions Explorer")
text("An interactive tool to explore NYC Motor Vehicle Collision data, focusing on person-level information.")

# Load the dataset
connect()  # Initialize connection to preswald.toml data sources
df = get_df("vehicle_collisions")  # Load the Motor Vehicle Collisions dataset

# Clean and prepare data
text("## Data Cleaning")
text("The original dataset contains some inconsistencies and missing values. The following cleaning steps were applied:")

# List the cleaning steps explicitly for visibility
text("1. Converting date fields to proper datetime format")
text("2. Converting age values to numeric and filtering out invalid ages")
text("3. Standardizing gender, person type, and injury status values")
text("4. Handling missing values appropriately")

# 1. Convert date to datetime
df['CRASH_DATE'] = pd.to_datetime(df['CRASH_DATE'], errors='coerce')

# 2. Convert PERSON_AGE to numeric, handling errors
df['PERSON_AGE'] = pd.to_numeric(df['PERSON_AGE'], errors='coerce')

# 3. Filter out invalid ages (keeping only ages between 0 and 100)
df = df[df['PERSON_AGE'].between(0, 100) | df['PERSON_AGE'].isna()]

# 4. Standardize PERSON_SEX values
df['PERSON_SEX'] = df['PERSON_SEX'].replace({'M': 'Male', 'F': 'Female', 'U': 'Unknown'})

# 5. Standardize PERSON_TYPE values
df['PERSON_TYPE'] = df['PERSON_TYPE'].fillna('Unknown').astype(str).str.title()

# 6. Standardize PERSON_INJURY values
df['PERSON_INJURY'] = df['PERSON_INJURY'].fillna('Unknown')
df['PERSON_INJURY'] = df['PERSON_INJURY'].replace({'Injured': 'Injured', 'Killed': 'Killed', 'Unspecified': 'No Injury/Unknown'})

# 7. Remove rows with missing key values
df = df.dropna(subset=['PERSON_TYPE'])

# Display dataset summary
text("## Dataset Overview")
text(f"This dataset contains {len(df):,} records of individuals involved in motor vehicle collisions in NYC.")

# Create summary statistics
text("## 1. Injury Statistics by Person Type")
injury_by_type = df.groupby('PERSON_TYPE')['PERSON_INJURY'].value_counts().unstack().fillna(0)
injury_by_type = injury_by_type.reset_index()
injury_by_type = injury_by_type.melt(id_vars=['PERSON_TYPE'], var_name='INJURY_STATUS', value_name='COUNT')

# Create visualization
fig1 = px.bar(injury_by_type, 
             x='PERSON_TYPE', 
             y='COUNT', 
             color='INJURY_STATUS',
             title="Injuries by Person Type",
             labels={
                 "PERSON_TYPE": "Person Type",
                 "COUNT": "Number of People",
                 "INJURY_STATUS": "Injury Status"
             })

# Style the plot
fig1.update_layout(template='plotly_white')

# Show the plot
plotly(fig1)

# Create a second visualization - Age distribution
text("## 2. Age Distribution of Involved Persons")
# Filter to valid ages
age_df = df[df['PERSON_AGE'].between(0, 100)].copy()

fig2 = px.histogram(age_df, 
                   x='PERSON_AGE',
                   color='PERSON_TYPE',
                   nbins=20,
                   title="Age Distribution by Person Type",
                   labels={
                       "PERSON_AGE": "Age",
                       "count": "Number of People",
                       "PERSON_TYPE": "Person Type"
                   })

# Style the plot
fig2.update_layout(template='plotly_white')

# Show the plot
plotly(fig2)

# Create a third visualization - Gender distribution by person type
text("## 3. Gender Distribution by Person Type")
gender_df = df[df['PERSON_SEX'].isin(['Male', 'Female'])].copy()
gender_counts = gender_df.groupby(['PERSON_TYPE', 'PERSON_SEX']).size().reset_index(name='COUNT')

fig3 = px.bar(gender_counts, 
             x='PERSON_TYPE', 
             y='COUNT', 
             color='PERSON_SEX',
             barmode='group',
             title="Gender Distribution by Person Type",
             labels={
                 "PERSON_TYPE": "Person Type",
                 "COUNT": "Number of People",
                 "PERSON_SEX": "Gender"
             })

# Style the plot
fig3.update_layout(template='plotly_white')

# Show the plot
plotly(fig3)

# Create a fourth visualization - Time of day analysis
text("## 4. Collisions by Time of Day")
# Extract hour from crash time - handle errors
try:
    # Make sure CRASH_TIME is a string
    df['CRASH_TIME'] = df['CRASH_TIME'].astype(str)
    # Extract hour safely
    df['CRASH_HOUR'] = df['CRASH_TIME'].str.split(':', expand=True)[0]
    # Convert to numeric, handling errors
    df['CRASH_HOUR'] = pd.to_numeric(df['CRASH_HOUR'], errors='coerce')
    
    # Group by hour and count
    hour_counts = df.dropna(subset=['CRASH_HOUR']).groupby('CRASH_HOUR').size().reset_index(name='COUNT')
    
    fig4 = px.line(hour_counts, 
                  x='CRASH_HOUR', 
                  y='COUNT',
                  markers=True,
                  title="Collisions by Hour of Day",
                  labels={
                      "CRASH_HOUR": "Hour of Day (24h)",
                      "COUNT": "Number of Collisions"
                  })
    
    # Style the plot
    fig4.update_layout(template='plotly_white', 
                      xaxis=dict(tickmode='linear', tick0=0, dtick=1))
    
    # Show the plot
    plotly(fig4)
except Exception as e:
    text("Could not create time of day visualization due to data issues.")
    # Create a simple alternative visualization
    text("Alternative visualization: Injury counts")
    injury_counts = df['PERSON_INJURY'].value_counts().reset_index()
    injury_counts.columns = ['Injury Status', 'Count']
    
    fig4_alt = px.pie(injury_counts, 
                     values='Count', 
                     names='Injury Status',
                     title="Distribution of Injury Status")
    plotly(fig4_alt)

# Create a fifth visualization - Safety equipment analysis for occupants
text("## 5. Safety Equipment Usage and Injury Outcomes")
try:
    # Filter to occupants only and where safety equipment is specified
    safety_df = df[(df['PERSON_TYPE'] == 'Occupant') & (df['SAFETY_EQUIPMENT'].notna()) & (df['SAFETY_EQUIPMENT'] != '')].copy()
    
    if len(safety_df) > 0:
        # Group by safety equipment and injury status
        safety_injury = safety_df.groupby(['SAFETY_EQUIPMENT', 'PERSON_INJURY']).size().reset_index(name='COUNT')
        
        # Get top 5 most common safety equipment types
        top_equipment = safety_df['SAFETY_EQUIPMENT'].value_counts().nlargest(5).index.tolist()
        safety_injury = safety_injury[safety_injury['SAFETY_EQUIPMENT'].isin(top_equipment)]
        
        fig5 = px.bar(safety_injury, 
                     x='SAFETY_EQUIPMENT', 
                     y='COUNT', 
                     color='PERSON_INJURY',
                     title="Safety Equipment Usage and Injury Outcomes",
                     labels={
                         "SAFETY_EQUIPMENT": "Safety Equipment",
                         "COUNT": "Number of People",
                         "PERSON_INJURY": "Injury Status"
                     })
        
        # Style the plot
        fig5.update_layout(template='plotly_white')
        
        # Show the plot
        plotly(fig5)
    else:
        text("Not enough data available for safety equipment analysis.")
        # Create an alternative visualization
        person_type_counts = df['PERSON_TYPE'].value_counts().reset_index()
        person_type_counts.columns = ['Person Type', 'Count']
        
        fig5_alt = px.bar(person_type_counts, 
                         x='Person Type', 
                         y='Count',
                         title="Distribution of Person Types")
        plotly(fig5_alt)
except Exception as e:
    text("Could not create safety equipment visualization due to data issues.")
    # Create a simple alternative visualization
    person_type_counts = df['PERSON_TYPE'].value_counts().reset_index()
    person_type_counts.columns = ['Person Type', 'Count']
    
    fig5_alt = px.bar(person_type_counts, 
                     x='Person Type', 
                     y='Count',
                     title="Distribution of Person Types")
    plotly(fig5_alt)

# Show a sample of the data
text("## Data Sample")
table(df.head(100), title="Motor Vehicle Collisions - Person Data (Sample)")
