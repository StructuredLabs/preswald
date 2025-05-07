
from preswald import text, plotly, connect, get_df, table, query, slider, selectbox
import pandas as pd
import plotly.express as px
# Load the CSV
connect() 
df = get_df('iris_data')
text("# Iris Dataset ")

table(df.head(10), title="Data Overview")

# Creating a scatter plot
text('Step 1: Creating visulaizations from the data ')

fig_1 = px.scatter(
    df,
    x="SepalLengthCm",
    y="SepalWidthCm",
    color="Species",
    title="Scatter Plot of sepal Dimensions[sepal_length(x-axis), sepal_widht(y-axis)]"
)

fig_1.update_layout(
    xaxis_title="Sepal Length (cm)",  
    yaxis_title="Sepal Width (cm)",
    title_x=0.5,  # Center the title
)
plotly(fig_1)

text('Step 2: Query or manipulate the data / the data is filtered accoding to the silder selection [the selected feature is sepal lenght]')

# Step 2.1: Add an interactive slider for Sepal Length filtering
threshold = slider("Minimum Sepal Length", min_val=4.0, max_val=8.0, default=5.0)

# Step 2.2: SQL Query to filter data based on the slider value
sql = f"SELECT * FROM iris_data WHERE SepalLengthCm > {threshold}"
filtered_df = query(sql, "iris_data")

# Step 2.3: Create a scatter plot of the **filtered** dataset
fig_2 = px.scatter(
    filtered_df,
    x="SepalLengthCm",
    y="SepalWidthCm",
    color="Species",
    title=f"Filtered Scatter Plot (Sepal Length > {threshold})"
)

fig_2.update_layout(
    xaxis_title="Sepal Length (cm)",
    yaxis_title="Sepal Width (cm)",
    title_x=0.5,
)
plotly(fig_2)

#######################################################

# step 3 : selecting features using selectbox. 

text(" Step 3: Filter the data accoding to a selected feature / select the feature from selectbox")

selected_feature = selectbox(
    "Select Feature for Filtering",
    options=["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"],
    default="SepalLengthCm"
)

feature_min = df[selected_feature].min()
feature_max = df[selected_feature].max()

text("Now select a range which you want the feature to be in from the slider")

threshold = slider(
    f"Filter {selected_feature} (Min: {feature_min}, Max: {feature_max})",
    min_val=float(feature_min),
    max_val=float(feature_max),
    default=float(feature_min)
)

text (" now selct the x and y axis for the plot you want in the filtered data")

x_axis = selectbox("Select X-Axis for Scatter Plot", 
                   options=["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"], 
                   default="SepalLengthCm")
y_axis = selectbox("Select Y-Axis for Scatter Plot", 
                   options=["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"], 
                   default="SepalWidthCm")

sql = f"SELECT * FROM iris_data WHERE {selected_feature} > {threshold}"
filtered_df = query(sql, "iris_data")

fig_3 = px.scatter(
    filtered_df,
    x=x_axis, 
    y=y_axis,  
    color="Species",
    title=f"Scatter Plot of {x_axis} vs {y_axis} (Filtered by {selected_feature} > {threshold})"
)

fig_3.update_layout(
    xaxis_title=x_axis.replace("Cm", " (cm)"),  
    yaxis_title=y_axis.replace("Cm", " (cm)"),
    title_x=0.5
)
plotly(fig_3)

table(filtered_df.head(10), title=f"Filtered Data from selection ({selected_feature} > {threshold})")
