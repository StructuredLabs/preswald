# Pokémon Stats Explorer: Interactive Insights & Visualizations  

## Overview  
Pokémon Stats Explorer is an interactive application built using **Preswald**, providing insights into Pokémon attributes such as **Attack, Speed, Weight, and Type distributions**. This app allows users to analyze Pokémon statistics using **dynamic scatter plots and bar charts**, with adjustable filters for in-depth exploration.  

## Dataset  
The dataset used in this project is the **Pokédex Dataset**, stored as a CSV file (`pokedex.csv`). It contains detailed information about **Pokémon attributes**, including:  

- **name**: Pokémon name  
- **type**: Pokémon type(s)  
- **attack**: Attack power rating  
- **defense**: Defensive rating  
- **speed**: Speed rating  
- **weight**: Pokémon's weight (kg)  
- **hp**: Hit Points (HP)  
- **run_length**: Evolution set  

### **Dataset Use Cases**  
- Identifying **high-attack and high-speed Pokémon**.  
- Understanding the **correlation between weight and attack power**.  
- Exploring **the distribution of Pokémon across different types**.  
- Comparing **top-rated Pokémon** across different attributes.  

**Dataset Link**: [Pokédex Dataset](https://www.kaggle.com/datasets/rzgiza/pokdex-for-all-1025-pokemon-w-text-description)  

---

## Features  

### **Interactive Filtering**
- Filter Pokémon by **Attack, Speed, Weight, and Type**.
- Adjust **minimum attack or speed thresholds** using **sliders**.
- Select the **number of top Pokémon** to display in rankings.

### **Dynamic Visualizations**
- **Scatter Plot:** Compare **Weight vs. Attack Power**.
- **Bar Chart:** View **Top N Pokémon by Attack Power**.
- **Scatter Plot:** Compare **Speed vs. Attack Power**.
- **Bar Chart:** Explore **Average Attack Power by Pokémon Type**.
- **Scatter Plot:** Analyze **Weight vs. Speed by Pokémon Type**.

### **Real-time Data Analysis**
- Pokémon stats update dynamically based on user selections.
- Instant filtering with smooth and interactive UI.
  
---

## How to Run Locally  

**Clone the repository**  
```sh
git clone https://github.com/menon-abhinav/preswald.git
cd preswald/community_gallery/pokedex_insights
