import asyncio
import pandas as pd
import plotly.express as px
import os
import psutil  # To check and kill running processes
import logging  # Enable debug logging
from fastapi import FastAPI
from preswald import query, text, plotly, connect, get_df, table, slider

DATASET_PATH = "data/my_dataset.csv"

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Ensure Uvicorn is not being started automatically
if "UVICORN_CMD" in os.environ:
    print("Uvicorn detected—this script does not use an ASGI app.")
    exit(1)

# Check and terminate other Uvicorn processes using port 8000
for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
    try:
        cmd = " ".join(proc.info["cmdline"]) if proc.info["cmdline"] else ""
        if "uvicorn" in cmd and "8000" in cmd:
            print(f"Terminating existing Uvicorn process (PID: {proc.info['pid']})")
            proc.terminate()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        continue

# Prevent multiple script reloads
if "SCRIPT_RELOADED" in os.environ:
    print("Script already reloaded. Exiting to prevent multiple reloads.")
    exit(0)
else:
    os.environ["SCRIPT_RELOADED"] = "1"

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI and Preswald!"}

# Try to start the Preswald Service manually
server_running = False
df = None
try:
    import preswald.engine.server_service as server_service
    print("Available functions in preswald.engine.server_service:", dir(server_service))

    if hasattr(server_service, 'ServerPreswaldService'):
        print("Found `ServerPreswaldService`. Attempting to initialize...")
        try:
            server_instance = server_service.ServerPreswaldService()
            if hasattr(server_instance, 'initialize'):
                print("Initializing ServerPreswaldService...")
                server_instance.initialize()
                print("ServerPreswaldService initialized successfully.")
                server_running = True
            elif hasattr(server_instance, 'get_instance'):
                print("Attempting `get_instance()` method...")
                server_instance = server_service.ServerPreswaldService.get_instance()
                print("ServerPreswaldService instance retrieved.")
                server_running = True
            else:
                print("No valid initialization method found in `ServerPreswaldService`.")
        except Exception as e:
            print(f"Failed to initialize ServerPreswaldService: {e}")
    else:
        print("No `ServerPreswaldService` found in preswald.engine.server_service.")
except ImportError as e:
    print(f"Error: Unable to import preswald.engine.server_service. Verify installation. Details: {e}")
except AttributeError as e:
    print(f"Error: Expected method not found in `server_service`. Details: {e}")
except Exception as e:
    print(f"Unexpected error initializing Preswald server: {e}")

# Load data manually from CSV if Preswald service fails
if not server_running:
    print("Server initialization failed. Running in client-only mode.")
    print("Warning: Running in client mode. Database features may not work.")

if os.path.exists(DATASET_PATH):
    print(f"Loading dataset from {DATASET_PATH}...")
    df = pd.read_csv(DATASET_PATH)
    
    expected_columns = {"VIN (1-10)", "County", "City", "State", "Postal Code", "Model Year", "Make", "Model", "Electric Vehicle Type", 
                        "Clean Alternative Fuel Vehicle (CAFV) Eligibility", "Electric Range", "Base MSRP", "Legislative District", 
                        "DOL Vehicle ID", "Vehicle Location", "Electric Utility", "2020 Census Tract"}
    if not expected_columns.issubset(df.columns):
        print(f"Error: Dataset missing expected columns: {expected_columns - set(df.columns)}")
        exit(1)

    print("Dataset loaded successfully.")
else:
    print(f"Error: `{DATASET_PATH}` not found. Please provide a valid dataset file.")
    exit(1)

# Attempt to fetch dataset from Preswald only if the server is running
if server_running:
    try:
        print("Connecting to Preswald...")
        conn = connect()
        print(f"Connection object: {conn}")
        if conn is None:
            print("Error: `connect()` returned None. Falling back to CSV data.")
        else:
            print("Fetching dataset...")
            df = get_df('dataset')
            if df is None or df.empty:
                print("Error: `get_df('dataset')` returned None or empty dataset. Falling back to CSV data.")
            else:
                print("Dataset fetched successfully from Preswald.")
    except Exception as e:
        print(f"Error connecting to Preswald services: {e}. Falling back to CSV data.")

# Ensure `df` is valid before continuing
if df is None or df.empty:
    print("Critical Error: No valid data loaded. Exiting script.")
    exit(1)

# Define `app` if missing
if not hasattr(server_service, "app"):
    print("Warning: `app` not found in `server_service`. Defining a dummy app.")
    app = FastAPI()
else:
    app = server_service.app

# Additional Debugging for ASGI app errors
if not hasattr(app, "router"):
    print("Critical Error: `app` in server_service is missing expected attributes. Exiting.")
    exit(1)

# Ensure `app` is set in `server_service`
server_service.app = app

# Filter EVs with an electric range > 50
filtered_df = df[df["Electric Range"] > 50]

# Setting a title of the page
text("# Electric Vehicle Data Analysis ")

# Create a table
table(filtered_df, title="Filtered Electric Vehicles")

# Add a custom visualization
text("## Electric Vehicle Data Analysis")

# Create a scatter plot
fig = px.scatter(df, x='Model Year', y='Electric Range', text='Make',
                 title='Electric Range by Model Year',
                 labels={'Model Year': 'Model Year', 'Electric Range': 'Electric Range (miles)'})

# Add labels to the plot
fig.update_traces(textposition='top center', marker=dict(size=12, color='green'))

# Style the plot
fig.update_layout(template='plotly_white')

# Display the plot
plotly(fig)

# Add a User Control Dynamic Data View
text("# Electric Range Threshold Analysis")

# Add a User Instruction
text("Please select the threshold value below to filter the vehicles based on Electric Range.")

# Set the values dynamically from the dataset
if not df.empty:
    threshold = slider("Electric Range Threshold", min_val=int(df["Electric Range"].min()),
                       max_val=int(df["Electric Range"].max()), default=100)
    table(filtered_df[filtered_df["Electric Range"] > threshold], title="Dynamic Electric Vehicle Data")

# Add a simple visualization
text("# Manufacturer-Based Analysis")

# Create a scatter plot
fig = px.scatter(filtered_df, x="Make", y="State", color="Electric Vehicle Type",
                 title="EV Type Distribution by Manufacturer")

# Display the plot
plotly(fig)