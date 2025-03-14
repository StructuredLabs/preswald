from preswald import connect, get_df, text, plotly, slider, selectbox, separator
import plotly.express as px
import pandas as pd

connect()
df = get_df("ec2_comparison")
text("# AWS EC2 Cost Optimization Dashboard")
text("Analyze EC2 instance pricing to find cost-saving opportunities. Compare On-Demand, Reserved, and Spot instance pricing to maximize your cloud budget efficiency.")

# Data Processing
try:
    viz_df = df.copy()
    for col in ["On Demand", "Linux Spot Minimum cost"]:
        if col in viz_df.columns:
            viz_df[col] = viz_df[col].astype(str).str.extract(r'(\d+\.\d+)').astype(float)
    
    viz_df["Monthly On Demand"] = viz_df["On Demand"] * 730
    viz_df["Monthly Spot"] = viz_df["Linux Spot Minimum cost"] * 730
    viz_df["Potential Savings"] = viz_df["Monthly On Demand"] - viz_df["Monthly Spot"]
    viz_df["Savings Percentage"] = (viz_df["Potential Savings"] / viz_df["Monthly On Demand"]) * 100
    viz_df['Family'] = viz_df['API Name'].str.split('.').str[0]
    viz_df["vCPU_Count"] = viz_df["vCPUs"].str.extract(r'(\d+)').astype(float)
    viz_df["Memory_GB"] = viz_df["Instance Memory"].str.extract(r'(\d+(?:\.\d+)?)').astype(float)
except Exception as e:
    text(f"Data processing issue: {str(e)}")

# Section 1: On-Demand vs Spot Pricing
text("## 1. On-Demand vs Spot Pricing")
num_instances = slider("Number of instances to display", min_val=5, max_val=20, default=10)
family_options = ["All Families"] + sorted(viz_df["Family"].unique().tolist())
selected_family = selectbox("Select Instance Family", options=family_options)

try:
    if selected_family != "All Families":
        family_filtered_df = viz_df[viz_df["Family"] == selected_family]
    else:
        family_filtered_df = viz_df
        
    top_instances = family_filtered_df.sort_values("Potential Savings", ascending=False).head(num_instances)
    
    fig1 = px.bar(
        top_instances,
        x="Name",
        y=["Monthly On Demand", "Monthly Spot"],
        title=f"Top {num_instances} Instances by Potential Savings: On-Demand vs Spot Pricing",
        barmode="group",
        labels={"value": "Monthly Cost ($)", "variable": "Pricing Type"}
    )
    
    fig1.update_layout(xaxis_tickangle=-45)
    plotly(fig1)
except Exception as e:
    text(f"Visualization issue: {str(e)}")

separator()

# Section 2: Cost Savings by Instance Family
text("## 2. Cost Savings by Instance Family")
try:
    family_savings = viz_df.groupby("Family")[["Savings Percentage"]].mean().reset_index()
    family_savings = family_savings.sort_values("Savings Percentage", ascending=False).head(10)
    
    fig2 = px.bar(
        family_savings,
        x="Family",
        y="Savings Percentage",
        color="Savings Percentage",
        color_continuous_scale="RdYlGn",
        title="Average Savings Percentage by Instance Family"
    )
    plotly(fig2)
except Exception as e:
    text(f"Visualization issue: {str(e)}")

separator()

# Section 3: Instance specifications analysis with slider
text("## 3. Instance Analysis")
min_vcpu = slider("Minimum vCPUs", min_val=1, max_val=64, default=1)
chart_type = selectbox("Select Chart Type", options=["Scatter Plot", "Bubble Chart"])

try:
    filtered_instances = viz_df[viz_df["vCPU_Count"] >= min_vcpu]
    major_families = ["t3", "m5", "c5", "r5"]
    major_instances = filtered_instances[filtered_instances["Family"].isin(major_families)]
    
    if chart_type == "Scatter Plot":
        fig3 = px.scatter(
            major_instances,
            x="vCPU_Count",
            y="Memory_GB",
            color="Family",
            title=f"vCPUs vs Memory by Instance Family (Min vCPUs: {min_vcpu})",
            labels={"vCPU_Count": "vCPUs", "Memory_GB": "Memory (GB)"}
        )
    else: 
        fig3 = px.scatter(
            major_instances,
            x="vCPU_Count",
            y="Memory_GB",
            color="Family",
            size="On Demand",
            hover_name="Name",
            title=f"vCPUs vs Memory by Instance Family (Min vCPUs: {min_vcpu})",
            labels={"vCPU_Count": "vCPUs", "Memory_GB": "Memory (GB)", "On Demand": "Hourly Cost ($)"}
        )
    plotly(fig3)
except Exception as e:
    text(f"Visualization issue: {str(e)}")

separator()

# Section 4: Network performance analysis with slider
text("## 4. Network Performance by Instance Family")
max_cost = slider("Maximum Hourly Cost ($)", min_val=0.01, max_val=5.0, default=1.0)
viz_type = selectbox("Select Visualization", options=["Bar Chart", "Heatmap"])

try:
    if 'Network Performance' in df.columns:
        cost_filtered_df = viz_df[viz_df["On Demand"] <= max_cost]
        network_pivot = cost_filtered_df.groupby(['Family', 'Network Performance']).size().reset_index(name='Count')
        top_families = cost_filtered_df['Family'].value_counts().head(8).index.tolist()
        network_pivot = network_pivot[network_pivot['Family'].isin(top_families)]
        
        if viz_type == "Bar Chart":
            fig4 = px.bar(
                network_pivot,
                x='Family',
                y='Count',
                color='Network Performance',
                title=f"Network Performance Options by Instance Family (Max Cost: ${max_cost})",
                barmode='group',
                labels={'Count': 'Number of Instances', 'Family': 'Instance Family'}
            )
        else:
            heatmap_data = network_pivot.pivot_table(
                values='Count', 
                index='Network Performance', 
                columns='Family', 
                fill_value=0
            )
            
            fig4 = px.imshow(
                heatmap_data,
                title=f"Network Performance Heatmap (Max Cost: ${max_cost})",
                labels=dict(x="Instance Family", y="Network Performance", color="Count"),
                color_continuous_scale="Viridis"
            )
        plotly(fig4)
    else:
        fig4 = px.scatter(
            viz_df[viz_df["On Demand"] <= max_cost],
            x='vCPU_Count',
            y='On Demand',
            color='Family',
            hover_name='Name',
            title=f"Hourly Cost vs vCPUs (Max Cost: ${max_cost})",
            labels={'vCPU_Count': 'vCPUs', 'On Demand': 'Hourly Cost ($)'}
        )
        plotly(fig4)
except Exception as e:
    text(f"Visualization issue: {str(e)}")

separator()