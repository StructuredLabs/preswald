import pandas as pd
from preswald import connect, get_df, text, table, slider, plotly
import plotly.express as px

# 1️⃣ Connect to the dataset
connect()
df = get_df("GlobalTemperatures")  # Ensure dataset matches preswald.toml

# 2️⃣ Convert 'dt' to a readable format (YYYY-MM)
df["dt"] = pd.to_datetime(df["dt"]).dt.strftime("%Y-%m")

# 3️⃣ Keep only relevant data (Year 2000 onwards)
df = df[df["dt"] >= "2000-01"]
df = df[["dt", "LandAverageTemperature"]]  # Keep only required columns

# 4️⃣ Ensure 'LandAverageTemperature' is numeric
df["LandAverageTemperature"] = pd.to_numeric(df["LandAverageTemperature"], errors="coerce")

# 5️⃣ Remove rows where `LandAverageTemperature` is missing
df = df.dropna(subset=["LandAverageTemperature"])

# 6️⃣ Sort by most recent date
df = df.sort_values(by="dt", ascending=False)

# 7️⃣ Display project title
text("# 🌍 Global Temperature Analysis")

# 8️⃣ Show a preview of the dataset
table(df.head(), title="Dataset Preview")

# 9️⃣ Interactive temperature filter
threshold = slider("Filter by Temperature (°C)", min_val=0, max_val=30, default=15)

# 🔟 Filtered data based on temperature
filtered_df = df[df["LandAverageTemperature"] > threshold]
table(filtered_df, title=f"Filtered Data (Temp > {threshold}°C)")

# 🔟 Create a visualization
fig = px.line(
    df,
    x="dt",
    y="LandAverageTemperature",
    title="🌡️ Global Temperature Over Time",
    labels={"dt": "Year-Month", "LandAverageTemperature": "Avg Temperature (°C)"},
)

plotly(fig)  # Display the plot
