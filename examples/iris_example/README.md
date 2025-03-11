# **Preswald Example App**

## **📌 Overview**
This is a simple **Preswald** app that demonstrates how to:
- Load and query the **Iris dataset**.
- Display an **interactive table**.
- Create a **scatter plot visualization** using `plotly.express`.
- Add **user controls** with a slider for dynamic filtering.

## **🚀 Features**
- 📊 **Data Querying**: Uses SQL to filter the dataset.
- 📈 **Interactive Visualization**: Plots a scatter plot of **Sepal Length vs Sepal Width**.
- 🎛 **User Controls**: Allows dynamic filtering with a **threshold slider**.
- 🗃 **Data Display**: Shows tables with both **original and filtered data**.

---

## **🛠 Setup & Installation**

### **1️⃣ Install Preswald**
Ensure you have **Preswald** installed. If not, install it using:
```bash
pip install preswald
```

### **2️⃣ Initialize Your Project**
If you haven't already, initialize a **Preswald project**:
```bash
preswald init my_example_project
cd my_example_project
```

### **3️⃣ Run the App Locally**
To start the application and view it in your browser:
```bash
preswald run
```
This will launch a **local server** where you can interact with the app.

---

## **📜 Code Explanation**
### **🔹 Import Required Modules**
```python
from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px
```
- **`text()`** → Displays text headings.
- **`connect()`** → Connects to data sources.
- **`get_df()`** → Loads the dataset.
- **`query()`** → Executes SQL queries.
- **`table()`** → Displays tables.
- **`slider()`** → Adds user input controls.
- **`plotly()`** → Displays interactive charts.

### **🔹 Load & Query Data**
```python
connect()
df = get_df('iris_csv')

sql = "SELECT * FROM iris_csv WHERE \"sepal.length\" > 5"
filtered_df = query(sql, "iris_csv")
```
- Loads the **Iris dataset**.
- Filters rows where `sepal.length > 5`.

### **🔹 Display Filtered Data Table**
```python
text("# My Data Analysis App")
table(filtered_df, title="Filtered Data")
```
- Displays the **filtered dataset** in a table.

### **🔹 Create Scatter Plot**
```python
fig = px.scatter(df, x='sepal.length', y='sepal.width', text='variety',
                 title='Iris Dataset: Sepal Length vs Width',
                 labels={'sepal.length': 'Sepal Length (cm)', 
                        'sepal.width': 'Sepal Width (cm)',
                        'variety': 'Species'})
```
- Creates a **scatter plot** with **Sepal Length vs Sepal Width**.

### **🔹 Add User Controls**
```python
threshold = slider("Sepal Length Threshold", min_val=0, max_val=8, default=5)
table(df[df["sepal.length"] > threshold], title="Dynamic Data View")
```
- Adds a **slider** for filtering based on **Sepal Length**.

### **🔹 Render the Scatter Plot**
```python
fig = px.scatter(df, x="sepal.length", y="sepal.width", color="variety")
plotly(fig)
```
- **Color codes** scatter plot points by species.
- Renders the **interactive plot** using `plotly`.

---

## **📤 Deployment**
### **Deploy to Preswald Cloud**
To deploy your app, run:
```bash
preswald deploy --target structured --github <your-github-username> --api-key <your-api-key>
```
- Replace `<your-github-username>` with your **GitHub username**.
- Replace `<your-api-key>` with your **Preswald API key**.

### **Deploy Using Docker**
If you prefer **self-hosting**, use Docker:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir preswald
CMD ["preswald", "run", "--host", "0.0.0.0", "--port", "8080"]
```
Then build & run:
```bash
docker build -t my-preswald-app .
docker run -p 8080:8080 my-preswald-app
```

---

## **🎯 Conclusion**
This **Preswald example app** demonstrates how to:
- Load and query datasets 📂
- Add interactivity with sliders 🎚
- Visualize data with `plotly` 📊

Happy coding! 🎉