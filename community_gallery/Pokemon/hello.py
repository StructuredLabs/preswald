from preswald import text, plotly, connect, get_df, table,selectbox,button
import pandas as pd
import plotly.express as px

text("# Manoj Assessment")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('pokemon_data')


#Table Listing

#filter fields for table display and rename columns
df_table_display = df[['name', 'japanese_name', 'type1', 'type2','classfication' ,'generation','is_legendary']].copy()

# Rename 'is_legendary' to 'Legendary' and convert 0/1 to No/Yes
df_table_display['Legendary'] = df_table_display['is_legendary'].map({0: 'No', 1: 'Yes', False: 'No', True: 'Yes'})
df_table_display = df_table_display.drop('is_legendary', axis=1)


# Add "Any" option to the type lists
primary_types = ["Any"] + df["type1"].unique().tolist()
secondary_types = ["Any"] + df["type2"].unique().tolist()

# Create selectboxes with "Any" option
primary_type = selectbox("Primary Type", primary_types, default="Any", size=0.5)
secondary_type = selectbox("Secondary Type", secondary_types, default="Any", size=0.5)


# Filter by primary type if selected and not "Any"
if primary_type and primary_type != "Any":
    df_table_display = df_table_display[df_table_display['type1'] == primary_type]

# Filter by secondary type if selected and not "Any"
if secondary_type and secondary_type != "Any":
    df_table_display = df_table_display[df_table_display['type2'] == secondary_type]

table(df_table_display,title="Pokemon Data")



#2D plots
selected_plot = selectbox("Select Plot", ["Type Distribution", "Type Comparison", "Legendary Distribution"])

if selected_plot == "Type Distribution":
    text("## Pokemon Type Distribution")
    # Count the occurrences of each primary type
    type_counts = df['type1'].value_counts().reset_index()



