import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from preswald import text, plotly, connect, get_df, table
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Title & Description
text("# Walmart Customer Purchases Analysis")
text("Analyze customer purchases with interactive insights and visualizations.")

# Load the dataset
connect()
df = get_df("walmart_csv")

text("## Data Overview")
text(f"**Rows:** {df.shape[0]}, **Columns:** {df.shape[1]}")

# Display raw data preview
table(df.head(10), title="Dataset Preview")

# Missing values check
missing_values = df.isnull().sum()
missing_values = missing_values[missing_values > 0]
if not missing_values.empty:
    text("**Missing Values Found:**")
    table(missing_values.to_frame(name="Missing Count"))

    # Fill missing values
    df.fillna(df.median(numeric_only=True), inplace=True)
else:
    text("**No missing values found in the dataset.**")



    # Histogram for Age
    fig_age = go.Figure(data=[go.Histogram(x=df['Age'], name='Age', marker=dict(color='skyblue'))])
    fig_age.update_layout(title='Distribution of Age', xaxis_title='Age', yaxis_title='Count')
    plotly(fig_age)

    # Histogram for Purchase Amount
    fig_purchase_amount = go.Figure(data=[go.Histogram(x=df['Purchase_Amount'], name='Purchase Amount', marker=dict(color='olive'))])
    fig_purchase_amount.update_layout(title='Distribution of Purchase Amount', xaxis_title='Purchase Amount', yaxis_title='Count')
    plotly(fig_purchase_amount)

    # Count Plot for Gender
    gender_counts = df['Gender'].value_counts()
    fig_gender = go.Figure(data=[go.Bar(x=gender_counts.index, y=gender_counts.values, marker=dict(colorscale='Viridis'))])
    fig_gender.update_layout(title='Count of Gender', xaxis_title='Gender', yaxis_title='Count')
    plotly(fig_gender)

    # Count Plot for Payment_Method
    payment_counts = df['Payment_Method'].value_counts()
    fig_payment_method = go.Figure(data=[go.Bar(x=payment_counts.index, y=payment_counts.values, marker=dict(colorscale='Magma'))])
    fig_payment_method.update_layout(title='Count of Payment Methods', xaxis_title='Payment Method', yaxis_title='Count')
    plotly(fig_payment_method)


    # Box Plot for Purchase Amount by Category
    fig_box = go.Figure()
    for category in df['Category'].unique():
        fig_box.add_trace(go.Box(
            y=df[df['Category'] == category]['Purchase_Amount'],
            name=str(category),
            boxmean='sd',
            marker=dict(color='lightblue')
        ))

    fig_box.update_layout(
        title='Purchase Amount by Category',
        xaxis_title='Category',
        yaxis_title='Purchase Amount',
        showlegend=False
    )

    plotly(fig_box)

    # Violin Plot for Rating by Gender
    fig_violin_rating_gender = go.Figure(data=[go.Violin(x=df['Gender'], y=df['Rating'], box_visible=True, line_color='blue')])
    fig_violin_rating_gender.update_layout(title='Rating Distribution by Gender', xaxis_title='Gender', yaxis_title='Rating')
    plotly(fig_violin_rating_gender)

df = pd.read_csv('data/Walmart_customer_purchases.csv')
# Convert categorical features to numerical values
df['Repeat_Customer'] = df['Repeat_Customer'].map({'Yes': 1, 'No': 0})
df['Discount_Applied'] = df['Discount_Applied'].map({'Yes': 1, 'No': 0})

# One-hot encode categorical features (Category & Payment Method)
df = pd.get_dummies(df, columns=['Category', 'Payment_Method'], drop_first=True)

# Scale numerical features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(df[['Age', 'Purchase_Amount', 'Discount_Applied', 'Repeat_Customer']])

# Convert back to DataFrame
df_scaled = pd.DataFrame(scaled_features, columns=['Age', 'Purchase_Amount', 'Discount_Applied', 'Repeat_Customer'])

# Finding the Optimal Number of Clusters
wcss = []  # Within-Cluster Sum of Squares
x_values = list(range(2, 11))  # Convert range to list

for k in x_values:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(df_scaled)
    wcss.append(kmeans.inertia_)

# Plot Elbow Method using Plotly
fig_elbow = go.Figure()
fig_elbow.add_trace(go.Scatter(
    x=x_values,
    y=wcss,
    mode='lines+markers',
    name='WCSS',
    line=dict(dash='dash', color='blue'),
    marker=dict(color='blue', size=8)
))

fig_elbow.update_layout(
    title='Elbow Method for Optimal K',
    xaxis_title='Number of Clusters',
    yaxis_title='WCSS',
    template='plotly_white',
    showlegend=False
)
plotly(fig_elbow)

text("We Got k=4 from elbow plot")

# Apply K-Means Clustering
optimal_k = 4  # Choose based on elbow plot
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df_scaled['Cluster'] = kmeans.fit_predict(df_scaled)

# Merge cluster labels with original dataset
df['Cluster'] = df_scaled['Cluster']

# Visualizing Customer Segments
pca = PCA(n_components=2)
pca_features = pca.fit_transform(df_scaled.drop(columns=['Cluster']))

df_scaled['PCA1'] = pca_features[:, 0]
df_scaled['PCA2'] = pca_features[:, 1]

# Scatter plot of clusters
fig_pca = px.scatter(df_scaled, x='PCA1', y='PCA2', color=df_scaled['Cluster'].astype(str),
                      title="Customer Segmentation (PCA Visualization)",
                      labels={'Cluster': 'Cluster ID'},
                      color_discrete_sequence=px.colors.qualitative.Vivid,
                      hover_data=df_scaled.columns)

fig_pca.update_layout(template='plotly_white')
plotly(fig_pca)

text( "High-Spending Repeat Customers (Cluster 0)")
text( "Discount-Sensitive Shoppers (Cluster 1)")
text("Budget-Conscious Shoppers (Cluster 2)")
text("Occasional High-Spenders (Cluster 3)")