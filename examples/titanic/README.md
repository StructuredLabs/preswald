# Preswald Project

# Titanic Survival Analysis Dashboard
## Overview
This interactive dashboard allows users to explore the famous Titanic dataset, analyzing how different factors influenced passenger survival rates during the disaster.

## Features
Data Exploration
View the initial dataset structure

Apply dynamic filtering based on age and fare thresholds

Examine filtered data in tabular format

Interactive Visualizations
Scatter Plot: Visualize the relationship between age, fare, and survival

Dashboard: View survival distribution and fare distribution by passenger class

3D Visualization: Explore the relationship between age, fare, family size, and survival

Sankey Diagram: Track passenger flow through different categories to survival outcomes

Correlation Heatmap: Analyze relationships between various features and survival

User Controls
Age and fare threshold sliders

Gender and passenger class filters

Point size and opacity controls for 3D visualization

Correlation method selection

Sorting options for correlation analysis

## Insights
The dashboard reveals several patterns in the Titanic disaster:

Women had significantly higher survival rates than men

Higher class passengers (1st class) were more likely to survive

Family size interacted with age and fare to influence survival probability

The Sankey diagram shows common paths to survival, such as Class 1 → Female → Adult → High Fare → Survived

## User Controls
Age and fare threshold sliders

Gender and passenger class filters

Point size and opacity controls for 3D visualization

Correlation method selection

Sorting options for correlation analysis

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run`