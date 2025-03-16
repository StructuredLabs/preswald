# Child BMI Data Visualization

## Dataset Source

This application uses a CSV file named **BMIData.csv** containing child BMI data collected from **2001 to 2023**. The dataset includes the following fields:

- **SchoolYear:** Academic year of the record.
- **NameHospital:** Hospital associated with the data.
- **Sex:** Gender information.
- **EpiUnderweight, EpiHealthyWeight, EpiOverweight, EpiObese:** Percentage values for various BMI categories.

## What the App Does

The application transforms and visualizes the BMI dataset to provide clear insights into child health trends over time. It:

- **Transforms the Data:**  
  Converts the raw, wide-format dataset into a long format so that different BMI categories can be compared side by side.
- **Aggregates the Data:**  
  Computes average BMI percentages for each school year and BMI category, summarizing the data for better clarity.
- **Visualizes the Data:**
  - **Grouped Bar Chart:** Displays the average distribution of BMI categories across all school years.
  - **Trend Line Chart:** Connects average BMI values over time with markers to highlight trends.
  - **Dynamic Filtering:** Provides a slider that lets users select a specific school year and view a detailed bar chart for that year.
- **Displays Data Tables:**  
  Presents both raw and aggregated data in table format for users interested in the underlying numbers.

## How to Run and Deploy

1. Install Preswald via pip: `pip install preswald`

2. Initialize a new project:  
   `preswald init my_project`  
   `cd my_project`

   This creates a folder named `my_project` with the basic files:

   - **hello.py:** Your main application file.
   - **preswald.toml:** Configuration for your app’s settings and style.
   - **secrets.toml:** Secure storage for API keys and sensitive information.
   - **.gitignore:** Preconfigured to exclude sensitive files.

3. Add the Application Code:  
   Replace the contents of `hello.py` with the BMI data visualization code. Ensure that the **BMIData.csv** file is available in your project’s data directory so that it can be accessed by the app.

4. Run the Application Locally:  
   Run `preswald run` to start the development server.  
   The app will typically be accessible at [http://localhost:8501](http://localhost:8501).

5. Deploy the Application:  
   Run `preswald deploy --target structured` to deploy your app to the Preswald cloud platform.  
   During the first deployment, you'll be prompted to authenticate with GitHub and enter your Preswald API key. Once deployed, your app will be accessible online at a URL provided by Preswald.
