
import pandas as pd
import plotly.express as px
from preswald import connect, get_df, table, text, plotly, slider
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Initialize connection to Preswald service
connect()

# Path to your dataset (this should be set in your preswald.toml as well)
data_file = "data/traffic_crashes/Traffic_Crashes_Crashes.csv"

# Load data using Pandas directly
df = pd.read_csv("/Users/chsmac/my_example_project/data/traffic_crashes/Traffic_Crashes_Crashes.csv")

# Ensure the dataframe is loaded correctly
if df is not None:
    text("Data loaded successfully!")

    # Data Cleaning and Preprocessing (handle NaN values and prepare for modeling)
    df = df.dropna(subset=['LATITUDE', 'LONGITUDE', 'INJURIES_TOTAL', 'CRASH_TYPE'])

    # EDA (Exploratory Data Analysis)
    # Scatter plot of traffic crashes by location and crash type
    fig = px.scatter(df, x="LATITUDE", y="LONGITUDE", color="CRASH_TYPE", title="Traffic Crashes by Location and Crash Type")
    plotly(fig)

    # Bar plot showing crash severity distribution
    severity_counts = df['INJURIES_TOTAL'].value_counts().reset_index()
    severity_counts.columns = ['Injuries', 'Count']
    fig2 = px.bar(severity_counts, x='Injuries', y='Count', title="Crash Injuries Distribution")
    plotly(fig2)

    # Pie chart for crash types distribution
    crash_type_counts = df['CRASH_TYPE'].value_counts().reset_index()
    crash_type_counts.columns = ['Crash Type', 'Count']
    fig3 = px.pie(crash_type_counts, names='Crash Type', values='Count', title="Distribution of Crash Types")
    plotly(fig3)

    # Pie chart for injuries total distribution
    injury_counts = df['INJURIES_TOTAL'].value_counts().reset_index()
    injury_counts.columns = ['Injuries Total', 'Count']
    fig4 = px.pie(injury_counts, names='Injuries Total', values='Count', title="Distribution of Total Injuries")
    plotly(fig4)

    # Prepare features for machine learning (Use relevant columns only)
    X = df[['LATITUDE', 'LONGITUDE', 'INJURIES_TOTAL']]
    y = df['CRASH_TYPE']

    # Train the RandomForest model (fit once for the session)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Option to check the model prediction accuracy
    check_model = slider("Check Model Accuracy (1 = Yes, 0 = No)", min_val=0, max_val=1, default=0)

    if check_model == 1:
        # Predict on the same data for testing purposes
        y_pred = model.predict(X)
        accuracy = accuracy_score(y, y_pred)
        text(f"Model accuracy: {accuracy * 100:.2f}%")

    # Get user inputs through sliders
    latitude_input = slider("Latitude", min_val=-90, max_val=90, default=41.816073)
    longitude_input = slider("Longitude", min_val=-180, max_val=180, default=-87.656743)
    injuries_input = slider("Injuries Total", min_val=0, max_val=10, default=0)

    # Prepare the input for prediction in the same format as training
    user_input = pd.DataFrame([[latitude_input, longitude_input, injuries_input]],
                              columns=['LATITUDE', 'LONGITUDE', 'INJURIES_TOTAL'])

    # Make the prediction
    try:
        predicted_severity = model.predict(user_input)
        text(f"Predicted crash type based on inputs: {predicted_severity[0]}")
    except Exception as e:
        text(f"Error during prediction: {str(e)}")

else:
    text("Failed to load data!")

