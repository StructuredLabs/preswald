from preswald import text, plotly, connect, get_df, table
import plotly.express as px
import pandas as pd
import io


us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "Virgin Islands, U.S.": "VI",
}


def preprocess(df):
    """Pre-Process Natality Dataset

    Args:
        df (pandas DataFrame): csv read of Natality dataset

    Returns:
        pandas DataFrame: column split dataset
    """
    cols = df.keys()[0].split('\t')
    cols = [c.replace('"', '') for c in cols]
    m = df[df.keys()[0]].astype('str').str.contains('\t')
    data = '\n'.join(df[m][df.keys()[0]].to_list())
    out = pd.read_csv(io.StringIO(data), sep='\t', names=cols)
    return out


def get_yearly_total(df):
    """Filter dataset by annual totals

    Args:
        df (pandas DataFrame): column split dataset

    Returns:
        _type_: filtered dataframe
    """
    return df[df['Notes'] == 'Total'][df['Year'].notna()]


def get_yearly_avg(df):
    """Return average age of mother for all years in dataset

    Args:
        df (pandas DataFrame): column split dataset

    Returns:
        pandas DataFrame: aggregated dataframe
    """
    out = df.groupby('State')['Average Age of Mother'].agg(['mean'])
    out = out.reset_index()
    out = out.rename(columns={'mean': 'Time Average Age of Mother'})
    return out.round(2)


text("## Natality Dataset Dashboard")
text('''
Visit [Births Data Summary](http://wonder.cdc.gov/wonder/help/natality.html)
for more information about this dataset.

Query Date: Mar 19, 2025
''')

connect()
df = get_df('natality')
df = preprocess(df)
std = df['Standard Deviation for Average Age of Mother']
df['SEM'] = std/(len(us_state_to_abbrev.keys()))**0.5
df = df.round(2)
totals = df[df['Notes'] == 'Total'][df['Year'].notna()]
yearly_average = get_yearly_avg(df)


text("### Average Age of Mother Over Time")
fig = px.line(totals, x='Year', y='Average Age of Mother',
              line_shape='spline', render_mode='svg',
              error_y='SEM',
              )
fig['data'][0]['line']['color'] = 'black'
fig.update_layout(template='plotly_white')
plotly(fig)

data = df[df['State'].notna()]
yearly_average['StateCode'] = yearly_average['State'].map(us_state_to_abbrev)

c1 = 'Average Age of Mother'
c2 = 'Fertility Rate'

data[c1] = pd.to_numeric(data[c1], errors="coerce")
data[c2] = pd.to_numeric(data[c2], errors="coerce")

text("### Time Average Age of Mother Across US")
fig = px.choropleth(data_frame=yearly_average,
                    locations=yearly_average['StateCode'],
                    locationmode='USA-states',
                    color='Time Average Age of Mother',
                    range_color=(25, 30),
                    color_continuous_scale='teal',
                    hover_name='State',
                    scope='usa')

plotly(fig)

text("### Average Age vs. Fertility Rate")
fig = px.scatter(data,
                 x="Average Age of Mother",
                 y="Fertility Rate",
                 hover_name='State',
                 trendline="ols",
                 color='Year',
                 color_continuous_scale='sunsetdark',
                 trendline_color_override='black',
                 hover_data=['Year', 'State']
                 )

fig.update_layout(template='plotly_white')
plotly(fig)

text('## Data')
table(data.round(2))

text('''
Dataset: Natality, 2007-2023

Query Parameters:
 - Year: 2013; 2014; 2015; 2016; 2017; 2018; 2019; 2020; 2021; 2022; 2023
 - Group By: Year; State
 - Show Totals: True
 - Show Zero Values: False
 - Show Suppressed: False
 - Calculate Rates Per: 1,000
 - Population Option: Default intercensal populations for years 2007-2009
''', size=1)
