from preswald import text, plotly, connect, get_df, table, slider
import plotly.express as px
from preswald import query, selectbox

text("# Kerala Rainfall Analysis - 2022")
text("### Original dataset shows the monthly, seasonal and annual rainfall of all met-run stations of Kerala, India in 2022 ")


# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')


#I am filtering out low-rainfall stations, because anyplace that receives below 1500mm should not be in Kerala(totally whimsical, I know) 
sql = "SELECT * FROM sample_csv WHERE Annual_Rainfall > 1500"
filtered_df = query(sql, "sample_csv")
text("#### Move the slider to dynamically filter the data based on Annual Rainfall. Only locations with more than 1500mm of rainfall are available.")

# Dynamic Data View
threshold = slider("Filter for Annual Rainfall", min_val=1500, max_val=5000, default=1500)
filtered_df_sorted = filtered_df[filtered_df["Annual_Rainfall"] > threshold].sort_values(by="Annual_Rainfall", ascending=False)
table(filtered_df_sorted, title="Dynamic Data View")

text("#### Monthly Rainfall Analysis")
text("Select a location to view the month wise rainfall for that location.")

# Selectbox for Location choice. All locations are available. 
location_choice = selectbox(
    label="Choose Location",
    options=filtered_df['Location'].unique().tolist(),
    default=filtered_df['Location'].unique().tolist()[0]
)


# Filter data for selected location. Based on the selected location, the data will be filtered
location_data = filtered_df[filtered_df['Location'] == location_choice]

# Bar Chart: Monthly Rainfall for Selected Location
monthly_columns = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
monthly_rainfall = location_data.melt(id_vars=['Location'], value_vars=monthly_columns, var_name='Month', value_name='Rainfall')

#Month wise Rainfall chart for the selected location
fig_monthly = px.bar(monthly_rainfall, x='Month', y='Rainfall', 
                     title=f'Monthly Rainfall for {location_choice}',
                     labels={'Rainfall': 'Total Rainfall (mm)'},
                     color='Rainfall',
                     color_continuous_scale='Greens')

plotly(fig_monthly)


# Bar Charts for Annual, Summer, SW Monsoon and NE Monsoon Rainfall for all locations
# Annual Rainfall
text("#### Overall Rainfall Analysis - Annual, Summer, SW Monsoon and NE Monsoon")
fig_annual = px.bar(filtered_df, x='Location', y='Annual_Rainfall', 
                 title='Annual Rainfall For all Locations', 
                 labels={'Annual_Rainfall': 'Total Annual Rainfall (mm)'},
                 color='Annual_Rainfall',
                 color_continuous_scale='Blues')

plotly(fig_annual)


fig_summer = px.bar(filtered_df, x='Location', y='Summer_Rainfall', 
                 title='Summer Rainfall For all Locations', 
                 labels={'Summer_Rainfall': 'Total Annual Rainfall (mm)'},
                 color='Summer_Rainfall',
                 color_continuous_scale='Blues')

plotly(fig_summer)

# SW Monsoon Rainfall
fig_swmonsoon = px.bar(filtered_df, x='Location', y='SW_Monsoon_Rainfall', 
                 title='South West Monsoon Rainfall For all Locations', 
                 labels={'SW_Monsoon_Rainfall': 'Total South West Monsoon Rainfall (mm)'},
                 color='SW_Monsoon_Rainfall',
                 color_continuous_scale='Blues')

plotly(fig_swmonsoon)

    
fig_nemonsoon = px.bar(filtered_df, x='Location', y='NE_Monsoon_Rainfall', 
                 title='North East Monsoon Rainfall For all Locations', 
                 labels={'NE_Monsoon_Rainfall': 'Total North East Monsoon Rainfall (mm)'},
                 color='NE_Monsoon_Rainfall',
                 color_continuous_scale='Blues')

plotly(fig_nemonsoon)



