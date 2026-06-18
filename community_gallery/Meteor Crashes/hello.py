from preswald import connect, get_df, plotly, slider, table, text, text_input, alert
import pandas as pd
import plotly.express as px

def clean_data(df):
    if df is not None:
        df.rename(columns={'mass (g)': 'mass'}, inplace=True)
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df.replace("", pd.NA, inplace=True)
        df['mass'] = pd.to_numeric(df['mass'], errors='coerce')
        clean_df = df.dropna(subset=['mass', 'reclat', 'reclong', 'name', 'id', 'nametype', 'recclass', 'fall', 'year', 'GeoLocation'])
        clean_df = clean_df[(clean_df[['name', 'id', 'nametype', 'recclass', 'fall', 'year', 'GeoLocation']].apply(lambda x: x != '').all(axis=1))]
        return clean_df
    else:
        alert("Failed to load dataset.", level="error")
        return None

def plot_data(df):
    if df is not None and not df.empty:
        fig = px.scatter_mapbox(df, 
                                lat='reclat', 
                                lon='reclong', 
                                hover_name='name',
                                hover_data={'year': True, 'mass': True},
                                size=df['mass'].apply(lambda x: x / 200000),       
                                color='year',
                                zoom=1,
                                mapbox_style="carto-positron",  
                                center={"lat": 24.7136, "lon": 46.6753},
                                title="Meteor Landings Around the World")
        return fig
    else:
        text("No valid mass data found.")
        return None
        
def range_data(df, start, end):
        if start and start.isdigit():
            df = df[df['year'] >  int(start)]
        elif start:
            alert("Enter a valid start year", level="warning")
        if end and end.isdigit():
            df = df[df['year'] < int(end)]
        elif end:
            alert("Enter a valid end year", level="warning")
        if not start and not end:
            df = df[(df['year'] > 2000) & (df['year'] < 2002)]
        return  df 
        

connect()
df = get_df('sample_csv')

text("# One Meteor a Crash! 🌠🔥💥", size=0.55)

if df is not None:
    text("To view Time Ranged Meteor Crashes Data add Dates!")
    rangeStart = text_input("Starting year for Range", placeholder="YYYY", size="0.5")
    rangeEnd = text_input("Ending year for Range", placeholder="YYYY", size="0.5")
    text(f"Showing data from Year {rangeStart or '2000'} to {rangeEnd or '2002'}")

    clean_df = clean_data(df)

    if clean_df is not None:
        clean_df = range_data(clean_df, rangeStart, rangeEnd)

        if not clean_df.empty:
            text("## Worldwide Crash Sites.")
            plotly(plot_data(clean_df))

            text("## A Closer Look at Each Meteor.")
            numberOfRowsToshow = slider("Slide Up to View more Meteors", min_val=5.0, default=5.0)
            table(clean_df, title="Meteorite Classification and Details", limit=numberOfRowsToshow)

            grouped = clean_df.groupby('recclass').size().reset_index(name='count')
            text("## Which Class of Meteorite Visits the Earth Most?")
            
            fig2 = px.pie(
                grouped, 
                names='recclass',        
                values='count',          
                title='Distribution of Meteorite Classifications', 
                hole=0.4,                
                width=800,               
                height=600                
            )   
            fig2.update_traces(textinfo='percent+label', pull=[0.1, 0.1, 0.1, 0.1, 0.1,0.1,0.1,0.1])
            plotly(fig2)
        else:
            text("No meteor data found in the specified range.")
    else:
        text("Failed to clean the dataset.")
else:
    text("Dataset not loaded or corrupted.")
