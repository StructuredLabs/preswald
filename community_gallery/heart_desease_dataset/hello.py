from preswald import connect,query,table,text,slider,get_df,plotly,table
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


text("# Welcome to Preswald!")

connect()  # Initialize connection to preswald.toml data sources
df = get_df("heart_csv")  # Load data
#sql = "SELECT * FROM my_dataset WHERE value > 50"
#filtered_df = query(sql,'heart_csv')

text("# My Data Analysis App")
#table(filtered_df, title="Filtered Data")

# fig = px.scatter(df, x="column1", y="column2", color="category")
# plotly(fig)

# fig = px.scatter(data_frame=df, x='RestingBP', y='MaxHR', text='Age',
#                  color='HeartDisease', color_continuous_scale=['green', 'red'],
#                  title='Resting Blood Pressure vs. Maximum Heart Rate',
#                  labels={'RestingBP': 'Resting Blood Pressure (mm Hg)', 
#                          'MaxHR': 'Maximum Heart Rate (bpm)',
#                          'HeartDisease': 'Heart Disease'},
#                  hover_data=['Age', 'Cholesterol', 'Oldpeak', 'ST_Slope'])

# # Add labels for each point
# fig.update_traces(textposition='top center', marker=dict(size=15))

# # Style the plot
# fig.update_layout(template='plotly_white',
#                   coloraxis_colorbar=dict(
#                       title='Heart Disease',
#                       tickvals=[0, 1],
#                       ticktext=['No', 'Yes']
#                   ))

# # To show the plot (this would replace the plotly(fig) function)
# #fig.show()

# plotly(fig)
# # To display the data as a table (this would replace the table(df) function)
# table(df)


def create_radar_chart():
    # Select numerical features to include
    features = ['Age', 'RestingBP', 'Cholesterol', 'MaxHR', 'Oldpeak']
    
    # Create a figure with subplots
    fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'polar'}]])
    
    # Normalize the data for better visualization
    df_norm = df.copy()
    for feature in features:
        max_val = df[feature].max()
        min_val = df[feature].min()
        # Avoid division by zero
        if max_val > min_val:
            df_norm[feature] = (df[feature] - min_val) / (max_val - min_val)
        else:
            df_norm[feature] = df[feature] / max_val
    
    # Add traces
    colors = ['green', 'red']
    for i, row in df_norm.iterrows():
        values = row[features].tolist()
        # Close the loop
        values.append(values[0])
        
        # Create list of angles
        theta = [f for f in features]
        theta.append(theta[0])
        
        # Create the trace
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=theta,
                fill='toself',
                name=f"Patient {i+1} ({'Heart Disease' if row['HeartDisease'] == 1 else 'No Heart Disease'})",
                line_color=colors[int(row['HeartDisease'])],
                fillcolor=colors[int(row['HeartDisease'])],
                opacity=0.6
            )
        )
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        title="Radar Chart of Patient Features",
        showlegend=True
    )
    
    return fig


radar_fig = create_radar_chart()
plotly(radar_fig) 
table(df)

# # Load the CSV
# connect() # load in all sources, which by default is the sample_csv
# df = get_df('heart_disease_risk_dataset_earlymed')

# # Create a scatter plot
# fig = px.scatter(df, x='quantity', y='value', text='item',
#                  title='Quantity vs. Value',
#                  labels={'quantity': 'Quantity', 'value': 'Value'})

# # Add labels for each point
# fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# # Style the plot
# fig.update_layout(template='plotly_white')

# # Show the plot
# plotly(fig)

# # Show the data
# table(df)
