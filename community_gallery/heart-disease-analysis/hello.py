from preswald import text, plotly, connect, get_df, table
import plotly.express as px

text("# Welcome to the Heart Disease Analysis App!🫀")
text("## This app provides insights into the heart disease dataset")

# Load the CSV
connect()  # load in all sources, which by default is the sample_csv
df = get_df("heart_csv")

table(title="Dataset Rows", data=df.head())


def remove_outliers(df, columns):
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    return df


# Columns to check for outliers
columns_to_check = ["age", "height", "weight", "ap_hi", "ap_lo"]
df = remove_outliers(df, columns_to_check)

# Recompute the correlation matrix
correlation_matrix = df.corr()

# Plot the correlation heatmap using Plotly
text("### Correlation Heatmap (Processed Data)")
fig_heatmap = px.imshow(
    correlation_matrix,
    text_auto=True,
    color_continuous_scale="armyrose",
    labels=dict(color="Correlation"),
)
plotly(fig_heatmap)

# Box plot for 'cardio' vs 'age'
text("### Age Distribution by Cardio Outcome (Processed Data)")
fig_box_age = px.box(df, x="cardio", y="age", points="all", color="cardio")
plotly(fig_box_age)

# Violin plot for 'cardio' vs 'cholesterol'
text("### Cholesterol Levels by Cardio Outcome (Processed Data)")
fig_violin_cholesterol = px.violin(
    df,
    x="cardio",
    y="cholesterol",
    color="cardio",
    box=True,
    points="all",
    labels={"cardio": "Cardio Outcome", "cholesterol": "Cholesterol Level"},
)
plotly(fig_violin_cholesterol)

# Scatter plot for 'ap_hi' vs 'ap_lo' colored by 'cardio'
text("### Systolic vs Diastolic Blood Pressure by Cardio Outcome (Processed Data)")
fig_scatter_bp = px.scatter(
    df,
    x="ap_hi",
    y="ap_lo",
    color="cardio",
    size="weight",
    hover_data=["age", "gender"],
    labels={
        "ap_hi": "Systolic Blood Pressure",
        "ap_lo": "Diastolic Blood Pressure",
        "cardio": "Cardio Outcome",
    },
)
fig_scatter_bp.update_layout(
    xaxis=dict(
        title="Systolic Blood Pressure",
        range=[df["ap_hi"].min() - 10, df["ap_hi"].max() + 10],
    ),
    yaxis=dict(
        title="Diastolic Blood Pressure",
        range=[df["ap_lo"].min() - 10, df["ap_lo"].max() + 10],
    ),
)
plotly(fig_scatter_bp)

# 3D Scatter plot for 'weight', 'age', and 'ap_hi' by 'cardio'
text(
    "### 3D Scatter Plot: Weight, Age, and Systolic Blood Pressure by Cardio Outcome (Processed Data)"
)
fig_3d_scatter = px.scatter_3d(
    df,
    x="weight",
    y="age",
    z="ap_hi",
    color="cardio",
    size="cholesterol",
    hover_data=["gender", "ap_lo"],
    labels={
        "weight": "Weight",
        "age": "Age",
        "ap_hi": "Systolic Blood Pressure",
        "cardio": "Cardio Outcome",
        "cholesterol": "Cholesterol Level",
    },
    title="3D Scatter Plot: Weight, Age, and Systolic Blood Pressure by Cardio Outcome",
)
fig_3d_scatter.update_traces(marker=dict(opacity=0.7))
plotly(fig_3d_scatter)

# Pair plot for selected features using Plotly
text("### Pair Plot for Selected Features (Processed Data)")
selected_features = [
    "age",
    "height",
    "weight",
    "ap_hi",
    "ap_lo",
    "cholesterol",
    "cardio",
]
fig_pairplot = px.scatter_matrix(
    df,
    dimensions=selected_features[:-1],  # Exclude 'cardio' from dimensions
    color="cardio",
    opacity=0.5,
    height=1000,
    labels={col: col.capitalize() for col in selected_features},
)
plotly(fig_pairplot)
