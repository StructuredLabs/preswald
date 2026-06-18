from preswald import connect, get_df, table, text, slider, plotly
import plotly.express as px
import plotly.graph_objects as go

# Initialize connection
connect()

# Load dataset
df = get_df("sample_csv")  # Ensure dataset name matches preswald.toml
print(df.shape)
rows = slider("Rows to Display", min_val=5, max_val=50, default=10)

# Display title
text("# Adult Income Analysis")

# User-controlled age threshold
threshold = slider("Age Threshold", min_val=18, max_val=40, default=30)

# Filter data based on age threshold
filtered_df = df[df["age"] > threshold]

# Display filtered data
table(filtered_df, title="Filtered Income Data (Age > Threshold)")

# Convert categorical columns to numerical codes
categorical_columns = ['workclass', 'education', 'marital-status', 'occupation', 
                       'relationship', 'race', 'gender', 'native-country', 'income']
for col in categorical_columns:
    df[col] = df[col].astype('category').cat.codes

# Create an interactive scatter plot (Education vs. Hours Per Week)
fig = px.scatter(df, x="education", y="hours-per-week", color="income", 
                 title="Education vs. Weekly Work Hours",
                 labels={"education": "Education Level", "hours-per-week": "Work Hours Per Week"})
plotly(fig)

# Add Histogram: Age Distribution
fig2 = px.histogram(df, x="age", color="income", 
                    title="Age Distribution by Income Level", 
                    labels={"age": "Age", "income": "Income Level"})
plotly(fig2)

# Add Box Plot: Hours Per Week by Income
fig3 = px.box(df, x="income", y="hours-per-week", 
              title="Work Hours Per Week by Income Level", 
              labels={"income": "Income Level", "hours-per-week": "Work Hours Per Week"})
plotly(fig3)

# Add Bar Chart: Count of Occupation by Income Level
# Group by occupation and income, but aggregate counts
occupation_counts = df.groupby(["occupation", "income"]).size().reset_index(name='count')
fig4 = px.bar(occupation_counts, x="occupation", y="count", color="income", 
              title="Occupation Count by Income Level", 
              labels={"occupation": "Occupation", "count": "Count of Occupation"})
fig4.update_xaxes(tickangle=45, tickmode='array')
plotly(fig4)

# Add Pie Chart: Proportion of Income Levels
fig5 = px.pie(df, names="income", title="Income Level Distribution")
plotly(fig5)

# Add a Heatmap: Correlation Matrix of Numerical Features
# Exclude categorical columns for correlation matrix
numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns
correlation_matrix = df[numerical_columns].corr()
fig6 = go.Figure(data=go.Heatmap(z=correlation_matrix.values, 
                                x=correlation_matrix.columns, 
                                y=correlation_matrix.columns, 
                                colorscale='Viridis'))
fig6.update_layout(title="Correlation Matrix Heatmap", 
                  xaxis_title="Features", yaxis_title="Features")
plotly(fig6)
