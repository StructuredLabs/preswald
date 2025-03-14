# Global Sustainable Energy Investigation 🌎
[Visit Deployed App Here](https://sustainability-energy-963320-ghaf3o10-ndjz2ws6la-ue.a.run.app)  
## Dataset
To download the main dataset, checkout [Kaggle's Global Data on Sustainable Energy](https://www.kaggle.com/datasets/anshtanwar/global-data-on-sustainable-energy)

For this project, the following features were used from the dataset: 
- Entity: The name of the country or region for which the data is reported.
- Year: The year for which the data is reported, ranging from 2000 to 2020.
- Access to electricity (% of population): The percentage of population with access to electricity.
- Electricity from fossil fuels (TWh): Electricity generated from fossil fuels (coal, oil, gas) in terawatt-hours.
- Electricity from nuclear (TWh): Electricity generated from nuclear power in terawatt-hours.
- Electricity from renewables (TWh): Electricity generated from renewable sources (hydro, solar, wind, etc.) in terawatt-hours.

## Objective
This project explores the world’s progress toward sustainable electricity access using the selected features. The two main objectives are:
1. Track Global Energy Trends: Users can explore how global energy usage has evolved over time by selecting different years and electricity sources. The results are visualized on a choropleth map.
2. Electricity Access Analysis: Users can select a country to visualize how the percentage of the population with electricity access has changed over time using a scatter plot.

## Run the App
1. Ensure you have Python 3.13.2 installed.
2. Install the required packages using (if not already installed):
    - ```pip install preswald pandas plotly```
3. Clone this repository 
    -  Ensure all files are in correct directory! Check the directory structure below
    ``` git clone <this-repo-url>
        cd sustainability_energy
    ```
4. Run the app locally! 
    - ```preswald run``` 

Here is the directory structure:
```
sustainability_energy/
├── data/
│   ├── globalDataEnergy.csv
├── hello.py
├── preswald.toml
├── pyproject.toml
├── README.md
```