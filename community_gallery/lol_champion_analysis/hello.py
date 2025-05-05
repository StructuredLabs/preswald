from preswald import text, plotly, table, connect, get_df, slider
import pandas as pd
import plotly.express as px

# Title
text("# 🏆 League of Legends Champion Analysis 🏆")
text("Explore champion attributes, roles, stats, range types, and resources in an interactive dashboard!")

# Load dataset using Preswald
connect()
df = get_df("lol_champions")

# Ensure DataFrame is loaded correctly
if df is not None and not df.empty:
    # Ensure 'damage' column is numeric
    df["be"] = pd.to_numeric(df["be"], errors="coerce")
    df = df.dropna(subset=["be"])
    df = df.drop(columns=["stats"], errors="ignore")  # Remove 'stats' column  # Remove rows with invalid 'damage' values
    
    # Introduction to Filtered Table
    text("## 🔍 Filtered Champions by Blue Essence Cost")
    text("This table filters champions based on their Blue Essence cost, helping players analyze affordability and value. By selecting a cost threshold, users can identify the most expensive and exclusive champions in the game.")
    text("This table shows champions with Blue Essence cost greater than the selected threshold.")
    
    # Interactive Slider (Enhanced UI)
    threshold = slider("🔹 Select Minimum Blue Essence Cost:",
        min_val=int(df["be"].min()),
        max_val=int(df["be"].max()),
        default=50,
        step=1  # Adjusted step for better control
    )
    from preswald import query
    sql = f"SELECT * FROM lol_champions WHERE be > {threshold}"
    dynamic_df = query(sql, "lol_champions")
    
    # Display Filtered Table
    if dynamic_df.empty:
        text("⚠️ No champions found with selected Blue Essence cost.")
    else:
        table(dynamic_df.drop(columns=['stats'], errors='ignore'), title="🔥 Filtered Champions by Blue Essence Cost")
    
    # Scatter Plot: Damage vs. Toughness (Interactive UI)
    text("## ⚔️ Champion Blue Essence vs. Toughness")
    text("This scatter plot compares a champion's Blue Essence cost to their toughness, revealing cost-effectiveness in terms of durability. Players can decide whether to invest in a tanky, high-cost champion or a more affordable but fragile alternative.")
    text("This scatter plot visualizes how toughness varies with Blue Essence cost among different champion roles.")
    fig1 = px.scatter(
        df, x='be', y='toughness', color='role', hover_name='apiname',
        title='Champion Blue Essence vs. Toughness',
        labels={'be': 'Blue Essence', 'toughness': 'Toughness', 'role': 'Role'},
        template='plotly_white', opacity=0.85, size_max=20
    )
    plotly(fig1)

    # Violin Plot: Damage Distribution by Range Type
    text("## 📊 Blue Essence Distribution by Range Type")
    text("This violin plot showcases the variation in Blue Essence cost among different range types, highlighting pricing trends for melee and ranged champions. It helps players understand which roles typically require higher in-game currency investments.")
    fig7 = px.violin(
        df, x='rangetype', y='be', color='rangetype',
        title='Blue Essence Distribution by Range Type',
        labels={'rangetype': 'Range Type', 'be': 'Blue Essence'},
        template='plotly_white', box=True
    )
    plotly(fig7)

    # Density Contour: Damage vs. Control
    text("## 🔥 Champion Blue Essence vs. Control Density")
    text("This density contour plot displays how a champion's Blue Essence cost correlates with their crowd control abilities. It identifies whether high-cost champions generally provide stronger crowd control compared to lower-cost ones.")
    text("This contour plot shows the concentration of champions based on Blue Essence cost and control values.")
    fig9 = px.density_contour(
        df, x='be', y='control', color='mobility',
        title='Champion Blue Essence vs. Control (Density)',
        labels={'be': 'Blue Essence', 'control': 'Control', 'mobility': 'Mobility'},
        template='plotly_white'
    )
    plotly(fig9)

    # Histogram: Damage Distribution
    text("## 📊 Blue Essence Cost Distribution")
    text("This histogram visualizes the spread of Blue Essence costs across all champions, showing how many champions fall into different pricing categories. It helps players determine if their desired champions fall into common or rare pricing brackets.")
    text("This histogram shows how champion Blue Essence cost values are distributed.")
    fig8 = px.histogram(
        df, x='be', color='role',
        title='Blue Essence Cost Distribution by Role',
        labels={'be': 'Blue Essence', 'role': 'Role'},
        template='plotly_white', opacity=0.8
    )
    plotly(fig8)

else:
    text("❌ Error: Dataset could not be loaded or is empty. Ensure data is correctly formatted.") 