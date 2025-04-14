# Preswald Project: Los Angeles Crime Report Analysis

This project is a data analysis and visualization app built using **Preswald**. It allows users to explore and analyze crime data from Los Angeles, providing interactive filters and visualizations.


Check it Out: https://my-project-240162-b8ouiawr-ndjz2ws6la-ue.a.run.app/
---

## Features

- **Dynamic Filters**:
  - Filter crimes by time of occurrence (`TIME OCC`).
  - Filter by crime type (`Crm Cd Desc`).
  - Filter by area (`AREA NAME`).
  - Filter by victim age (`Vict Age`).
  - Filter by weapon used (`Weapon Desc`).

- **Visualizations**:
  - Scatter plot of crime locations.
  - Bar chart of crime counts by area.
  - Pie chart of crime types in a selected area.
  - Histogram of crime types for a selected victim age.
  - Scatter plot of crime locations for a selected weapon.


---

## Setup

```markdown
LA_crime_repor/
├── preswald.toml          
├── secrets.toml           
├── LACrimeReport.py       
├── data/                  
│   └── LACrimeReport.csv  
└── README.md              
```

---

## Run the Application

1. **Install Dependencies**:
   - Install the Preswald library:
     ```bash
     pip install preswald
     ```
   - Install Plotly for visualizations:
     ```bash
     pip install plotly
     ```

2. **Navigate to the Project Directory**:
   ```bash
   cd community_gallery/LA_crime_report
   ```
3. **Run**:
   ```bash
   preswald run
   ```