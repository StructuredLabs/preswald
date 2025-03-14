# Preswald Project

# Titanic Survival Analysis Dashboard
## Overview
This project is a dynamic dashboard for visualizing and analyzing the Titanic dataset. The Titanic dataset is a well-known dataset from the Titanic disaster of 1912, which contains information about the passengers aboard the Titanic. This dashboard allows you to explore various relationships and distributions within the data.

## Dataset Description
The Titanic dataset contains the following key columns:

- PassengerId: A unique identifier for each passenger.
- Pclass: The class of the ticket the passenger purchased (1st, 2nd, or 3rd).
- Name: The name of the passenger.
- Sex: The gender of the passenger (Male/Female).
- Age: The age of the passenger.
- SibSp: The number of siblings or spouses aboard the Titanic.
- Parch: The number of parents or children aboard the Titanic.
- Ticket: The ticket number.
- Fare: The fare the passenger paid for the ticket.
- Cabin: The cabin the passenger stayed in.
- Embarked: The port where the passenger boarded the Titanic (C = Cherbourg; Q = Queenstown; S = Southampton).
- Survived: A binary indicator of whether the passenger survived (1 = Survived, 0 = Died).

## Visualizations
The dashboard contains multiple visualizations to explore the Titanic dataset dynamically. These visualizations provide insights into various factors affecting passenger survival and their relationships with other features.

1. Pie Charts
The dashboard includes different pie charts that display the survival percentage based on the following factors:

- Survival by Sex: Shows the percentage of male and female survivors.
- Survival by Age: Displays the survival rate segmented by age groups (e.g., Child, Adult, Elderly).
- Survival by Embarked Port: Shows survival rates based on the port where passengers boarded (Cherbourg, Queenstown, Southampton).
- Survival by Ticket Class: Shows survival rates segmented by the class of the ticket purchased (1st, 2nd, 3rd).

Each of these pie charts includes dynamic filters that allow you to update the chart based on additional selections. These filters allow you to explore how the survival rate changes under different conditions.

2. Correlation Matrix
The dashboard also includes a correlation matrix that shows the relationships between different features in the dataset. This matrix highlights the dependencies between numerical features (e.g., Age, Fare, SibSp, Parch) and helps in understanding how these variables relate to each other. It also shows how various factors are correlated with survival.

3. Dynamic Relation Plots
The dashboard features dynamic relation plots that explore the relationship between Age and Fare across different selectable factors. These plots allow you to analyze how survival and other factors (e.g., Port of Embarkation, Sex, or Survived/Died) influence the relationship between age and fare. The user can choose which factors to plot and see how the data changes dynamically.

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run`