# Chicago Crime Dashboard

## Dataset Source

This application uses the Chicago Crime Dataset 2025, which contains reported incidents of crime that occurred in the City of Chicago. The dataset is derived from the Chicago Police Department's CLEAR (Citizen Law Enforcement Analysis and Reporting) system.
Link: [Chicago crime dataset 2025](https://data.cityofchicago.org/Public-Safety/Crimes-2022/9hwr-2zxp/about_data)

The dataset includes the following information for each crime incident:
- Date and time of occurrence
- Type of crime and description
- Location (block, coordinates, etc.)
- Whether an arrest was made
- District, ward, and community area information
- Geographic coordinates

## What This App Does

The Chicago Crime Dashboard is an interactive data visualization tool that allows users to explore crime patterns in Chicago. The application offers:

1. **Overview of Crime Types**: Visual breakdown of the most common types of crimes
2. **Location Analysis**: Shows where crimes most frequently occur
3. **Simple Filtering**: Ability to filter crime data by type
4. **Data Table**: Displays detailed crime records with essential information

This simple dashboard helps users identify patterns and trends in crime data, making it easier to understand the nature and distribution of criminal activities across Chicago.

## How to Run and Deploy

### Prerequisites

- Python 3.9 or higher
- Preswald library

### Installation

   ```
   pip install preswald 
   ```

### Running the App

Run the application using the Preswald CLI:

```
preswald run app.py
```

### Deployment

To deploy the application:

   Package your application:
   ```
   preswald deploy
   ```