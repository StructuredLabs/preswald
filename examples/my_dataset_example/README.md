My Dataset Example - Preswald

======= Dataset Source =======

This example demonstrates the use of Preswald for analyzing electric vehicle data.
The dataset my_dataset.csv contains information on electric vehicles, including:

VIN, County, City, State

Model Year, Make, Model

Electric Vehicle Type, Clean Alternative Fuel Vehicle (CAFV) Eligibility

Electric Range, Base MSRP, Legislative District

Vehicle Location, Electric Utility, 2020 Census Tract

Source: (If applicable, mention the dataset source or provide a link)

====== About This App ======

This app loads and analyzes electric vehicle data using Preswald and FastAPI.
It includes:

A table displaying EVs with an electric range greater than 50 miles.

Interactive visualizations using Plotly.

Dynamic filters based on vehicle attributes.

How to Run This Example

====== Clone the Preswald Repository ======

git clone https://github.com/<your-repo>/preswald.git
cd preswald/examples/my_dataset_example

======= Install Dependencies =======

pip install -r requirements.txt

======= Run the App ======

python hello.py

or, if using Uvicorn:

uvicorn hello:app --reload

===== Access the App =======

Once running, the app will be available at:

http://localhost:8000

==========Notes===========

Ensure my_dataset.csv is available in the data/ folder.

If using a database instead of CSV, update hello.py accordingly.
