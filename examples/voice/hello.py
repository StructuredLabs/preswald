from preswald import text, plotly, slider, selectbox, view
import pandas as pd
import duckdb
import plotly.express as px

# 📌 Color Configuration
COLOR_PALETTE = {
    'primary': '#1e3d58',      
    'secondary': '#057dcd',    
    'tertiary': '#43b0f1',     
    'quaternary': '#e8eef1',  
}

# Color sequences for different chart types
COLOR_SEQUENCE = list(COLOR_PALETTE.values())
HEATMAP_COLORS = "Blues"           # For density heatmaps
CORRELATION_COLORS = "RdBu_r"      # For correlation matrices

# Color sequences for different chart types
COLOR_SEQUENCE = list(COLOR_PALETTE.values())
CONTINUOUS_COLORS = [
    [0, COLOR_PALETTE['quaternary']],    # Red for negative correlations
    [0.5, '#ffffff'],                    # White for no correlation
    [1, COLOR_PALETTE['primary']]        # Blue for positive correlations
]

# 📌 Step 1: Dashboard Title
text("# Voice Agent Analytics")

# Load AI logs
asr_logs = pd.read_json("data/asr_logs.json")
intent_logs = pd.read_csv("data/intent_logs.csv")
response_logs = pd.read_csv("data/response_logs.csv")

# Create DuckDB connection
con = duckdb.connect()
con.register("asr_logs", asr_logs)
con.register("intent_logs", intent_logs)
con.register("response_logs", response_logs)

# Perform optimized SQL join
query = """
SELECT 
    a.call_id, 
    a.transcribed_text, 
    a.asr_confidence, 
    i.user_said, 
    i.predicted_intent, 
    i.intent_confidence, 
    r.ai_response, 
    r.response_time, 
    r.timestamp
FROM asr_logs a
JOIN intent_logs i ON a.call_id = i.call_id
JOIN response_logs r ON a.call_id = r.call_id
"""

merged_logs = con.execute(query).fetchdf()
merged_logs["timestamp"] = pd.to_datetime(merged_logs["timestamp"])

# 📌 Step 4: ASR vs Intent Confidence Scatter Plot
text("### 🎯 ASR vs Intent Classification Confidence")
text("Does poor speech recognition affect intent classification? Use the slider to filter.")

asr_confidence_threshold = slider(
    label="Minimum ASR Confidence",
    min_val=0,
    max_val=1,
    step=0.1,
    default=0.5
)["value"]

filtered_logs = merged_logs[merged_logs["asr_confidence"]
                            >= asr_confidence_threshold]

fig1 = px.scatter(
    filtered_logs,
    x="asr_confidence",
    y="intent_confidence",
    color="predicted_intent",
    title="ASR Confidence vs Intent Classification Confidence",
    hover_data=["transcribed_text", "user_said"],
    color_discrete_sequence=COLOR_SEQUENCE
)

fig1.update_layout(
    dragmode=False,  # Disable zoom & pan
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale", "resetScale", "orbitRotation", "tableRotation"],  # Remove menu buttons
    scene_camera_eye=dict(x=0, y=0, z=1)  # Reset camera (for 3D plots)
)

plotly(fig1)

# 📌 Step 5: Misclassification Heatmap
text("### 🔥 Misclassification Heatmap")
text("This heatmap highlights how frequently intents are misclassified.")

fig2 = px.density_heatmap(
    merged_logs[merged_logs["predicted_intent"] != merged_logs["user_said"]],
    x="predicted_intent",
    y="user_said",
    title="Misclassification Heatmap",
    labels={"predicted_intent": "Predicted Intent",
            "user_said": "Actual Intent"},
    color_continuous_scale=CONTINUOUS_COLORS,
)

fig2.update_layout(
    dragmode=False,  # Disable zoom & pan
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale", "resetScale", "orbitRotation", "tableRotation"],  # Remove menu buttons
    scene_camera_eye=dict(x=0, y=0, z=1)  # Reset camera (for 3D plots)
)

plotly(fig2)

# 📌 Step 6: AI Response Time Analysis (Box Plot)
text("### ⏳ AI Response Time by Intent")
text("Do certain intents take longer for the AI to respond to? This box plot helps detect slow responses and outliers.")

fig3 = px.box(
    merged_logs,
    x="predicted_intent",
    y="response_time",
    title="AI Response Time by Intent",
    labels={"predicted_intent": "Predicted Intent",
            "response_time": "Response Time (seconds)"},
    color="predicted_intent",
    points="all",
    color_discrete_sequence=COLOR_SEQUENCE
)

fig3.update_layout(
    dragmode=False,  # Disable zoom & pan
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale", "resetScale", "orbitRotation", "tableRotation"],  # Remove menu buttons
    scene_camera_eye=dict(x=0, y=0, z=1)  # Reset camera (for 3D plots)
)

plotly(fig3)

# 📌 Step 8: Intent Confidence Distribution (Violin Plot)
text("### 📊 Intent Confidence Distribution by Intent")
text("This violin plot shows the spread of confidence levels for each intent category.")

fig7 = px.violin(
    merged_logs,
    x="predicted_intent",
    y="intent_confidence",
    box=True,
    points="all",
    title="Intent Confidence Distribution by Intent",
    labels={"predicted_intent": "Predicted Intent",
            "intent_confidence": "Intent Confidence"},
    color="predicted_intent",
    color_discrete_sequence=COLOR_SEQUENCE
)

fig7.update_layout(
    dragmode=False,  # Disable zoom & pan
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale", "resetScale", "orbitRotation", "tableRotation"],  # Remove menu buttons
    scene_camera_eye=dict(x=0, y=0, z=1)  # Reset camera (for 3D plots)
)

plotly(fig7)

# 📌 Step 9: Response Time Distribution (Histogram)
text("### 📈 Response Time Distribution")
text("This histogram shows the distribution of AI response times.")

fig8 = px.histogram(
    merged_logs,
    x="response_time",
    title="Distribution of AI Response Times",
    labels={"response_time": "Response Time (seconds)"},
    nbins=30,
    color_discrete_sequence=COLOR_SEQUENCE
)

fig8.update_layout(
    dragmode=False,  # Disable zoom & pan
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale", "resetScale", "orbitRotation", "tableRotation"],  # Remove menu buttons
    scene_camera_eye=dict(x=0, y=0, z=1)  # Reset camera (for 3D plots)
)

plotly(fig8)

# 📌 Step 10: Correlation Matrix Heatmap
text("### 🔄 Correlation Matrix Heatmap")
text("How do ASR confidence, intent confidence, and response time relate to each other? This heatmap reveals correlations.")

correlation_matrix = merged_logs[[
    "asr_confidence", "intent_confidence", "response_time"]].corr()

fig9 = px.imshow(
    correlation_matrix,
    text_auto=True,
    # color_continuous_scale="RdBu_r",
    title="Correlation Matrix: ASR Confidence, Intent Confidence, Response Time",
    labels=dict(x="Metrics", y="Metrics"),
    color_continuous_scale=CONTINUOUS_COLORS,
)

fig9.update_layout(
    dragmode=False,  # Disable zoom & pan
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale", "resetScale", "orbitRotation", "tableRotation"],  # Remove menu buttons
    scene_camera_eye=dict(x=0, y=0, z=1)  # Reset camera (for 3D plots)
)

plotly(fig9)


# Add hierarchical view of intents and confidence
fig_sunburst = px.sunburst(
    merged_logs,
    path=['predicted_intent'],
    values='intent_confidence',
    title="Intent Distribution and Confidence Levels",
    color_discrete_sequence=COLOR_SEQUENCE
)

fig_sunburst.update_layout(
    dragmode=False,  # Disable zoom & pan
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale", "resetScale", "orbitRotation", "tableRotation"],  # Remove menu buttons
    scene_camera_eye=dict(x=0, y=0, z=1)  # Reset camera (for 3D plots)
)

plotly(fig_sunburst)

# Add performance metrics grid
metrics_df = pd.DataFrame({
    'Metric': ['Avg ASR Confidence', 'Avg Intent Confidence', 'Avg Response Time'],
    'Value': [
        merged_logs['asr_confidence'].mean(),
        merged_logs['intent_confidence'].mean(),
        merged_logs['response_time'].mean()
    ]
})

fig_metrics = px.bar(
    metrics_df,
    x='Metric',
    y='Value',
    title="Key Performance Metrics",
    color_discrete_sequence=COLOR_SEQUENCE
)

fig_metrics.update_layout(
    dragmode=False,  # Disable zoom & pan
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale", "resetScale", "orbitRotation", "tableRotation"],  # Remove menu buttons
    scene_camera_eye=dict(x=0, y=0, z=1)  # Reset camera (for 3D plots)
)

plotly(fig_metrics)

# Analyze AI response patterns
response_patterns = merged_logs.groupby('ai_response').agg({
    'response_time': 'mean',
    'intent_confidence': 'mean',
    'call_id': 'count'
}).reset_index()

fig_patterns = px.scatter(
    response_patterns,
    x='response_time',
    y='intent_confidence',
    size='call_id',
    hover_data=['ai_response'],
    title="Response Pattern Analysis",
    color_discrete_sequence=COLOR_SEQUENCE
)

fig_patterns.update_layout(
    dragmode=False,  # Disable zoom & pan
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale", "resetScale", "orbitRotation", "tableRotation"],  # Remove menu buttons
    scene_camera_eye=dict(x=0, y=0, z=1)  # Reset camera (for 3D plots)
)

plotly(fig_patterns)

# Create binned ASR confidence levels
merged_logs['asr_bin'] = pd.qcut(merged_logs['asr_confidence'], q=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])

fig_impact = px.box(
    merged_logs,
    x='asr_bin',
    y='intent_confidence',
    color='predicted_intent',
    title="ASR Quality Impact on Intent Classification",
    color_discrete_sequence=COLOR_SEQUENCE
)
fig_impact.update_layout(
    dragmode=False,  # Disable zoom & pan
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale", "resetScale", "orbitRotation", "tableRotation"],  # Remove menu buttons
    scene_camera_eye=dict(x=0, y=0, z=1)  # Reset camera (for 3D plots)
)
plotly(fig_impact)

# Analyze patterns in low confidence cases
low_confidence = merged_logs[
    (merged_logs['asr_confidence'] < merged_logs['asr_confidence'].median()) |
    (merged_logs['intent_confidence'] < merged_logs['intent_confidence'].median())
]

fig_errors = px.scatter_matrix(
    low_confidence,
    dimensions=['asr_confidence', 'intent_confidence', 'response_time'],
    color='predicted_intent',
    title="Error Pattern Analysis",
    color_discrete_sequence=COLOR_SEQUENCE
)

fig_errors.update_layout(
    dragmode=False,  # Disable zoom & pan
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale", "resetScale", "orbitRotation", "tableRotation"],  # Remove menu buttons
    scene_camera_eye=dict(x=0, y=0, z=1)  # Reset camera (for 3D plots)
)
plotly(fig_errors)

# Create satisfaction score based on multiple metrics
merged_logs['satisfaction_score'] = (
    merged_logs['asr_confidence'] * 0.3 +
    merged_logs['intent_confidence'] * 0.4 +
    (1 - merged_logs['response_time']/merged_logs['response_time'].max()) * 0.3
)

fig_satisfaction = px.histogram(
    merged_logs,
    x='satisfaction_score',
    color='predicted_intent',
    marginal='box',
    title="Customer Satisfaction Score Distribution",
    color_discrete_sequence=COLOR_SEQUENCE
)
fig_satisfaction.update_layout(
    dragmode=False,  # Disable zoom & pan
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale", "resetScale", "orbitRotation", "tableRotation"],  # Remove menu buttons
    scene_camera_eye=dict(x=0, y=0, z=1)  # Reset camera (for 3D plots)
)
plotly(fig_satisfaction)


# 📌 Step 12: View Transformed Data
text("## 📑 View Transformed AI Logs")
text("Below is the final dataset after merging ASR transcriptions, intent classifications, and AI responses.")

view(merged_logs, limit=20)


