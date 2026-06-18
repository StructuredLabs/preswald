import pandas as pd
import plotly.express as px

# Load dataset
file_path = r"C:\Users\Office\Desktop\Ashwitha\ev-population-analytics\data\Electric_Vehicle_Population_Data.csv"

df = pd.read_csv(file_path)

# Normalize column names
df.columns = [col.strip().replace(" ", "_").lower() for col in df.columns]

# Ensure 'registration_count' exists
if "registration_count" not in df.columns:
    df["registration_count"] = df.groupby(["make", "model"])["vin_(1-10)"].transform("count")

# EV Registrations by Make
fig1 = px.bar(df, x="make", y="registration_count", color="make",
              title="Electric Vehicle Registrations by Make", 
              labels={"make": "Car Manufacturer", "registration_count": "Number of Registrations"},
              height=500)
fig1.show()

# EV Registrations by Model Year
fig2 = px.histogram(df, x="model_year", nbins=15, color="make",
                    title="EV Registrations Over the Years", 
                    labels={"model_year": "Year", "count": "Number of Vehicles"},
                    height=500)
fig2.show()

# EV Distribution by City
top_cities = df["city"].value_counts().nlargest(10).reset_index()
fig3 = px.bar(top_cities, x="index", y="city",
              title="Top 10 Cities with Most EV Registrations", 
              labels={"index": "City", "city": "Number of Registrations"},
              height=500)
fig3.show()

# EVs by Electric Vehicle Type
fig4 = px.pie(df, names="electric_vehicle_type", title="Electric Vehicle Types Distribution")
fig4.show()

# EVs with Longest Electric Range (Ensure 'electric_range' exists)
if "electric_range" in df.columns:
    top_ev_range = df.nlargest(10, "electric_range")[["make", "model", "electric_range"]]
    fig5 = px.bar(top_ev_range, x="model", y="electric_range", color="make",
                  title="Top 10 EVs with Longest Electric Range", 
                  labels={"model": "EV Model", "electric_range": "Range (miles)"},
                  height=500)
    fig5.show()
else:
    print("Column 'electric_range' not found in dataset.")
