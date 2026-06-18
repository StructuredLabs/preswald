import pandas as pd
import os
from preswald import connect, get_df, slider, table, text, plotly
import plotly.express as px

if not os.path.exists("data/iris.csv"):
    from sklearn.datasets import load_iris
    iris = load_iris()
    iris_df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
    iris_df['species'] = [iris.target_names[i] for i in iris.target]
    
    os.makedirs("data", exist_ok=True)
    
    iris_df.to_csv("data/iris.csv", index=False)
    
    with open("preswald.toml", "a") as f:
        f.write('\n[data.iris]\npath = "data/iris.csv"\n')

try:
    connect()
    df = get_df("iris")
    
    if df is None:
        print("Using pandas to load data directly as a fallback")
        df = pd.read_csv("data/iris.csv")
except Exception as e:
    print(f"Error during initialization: {e}")
    df = pd.read_csv("data/iris.csv")

if 'sepal length (cm)' in df.columns:
    df.columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']
elif len(df.columns) == 5:
    df.columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']

text("# Iris Dataset Analysis")

threshold = slider("Minimum Petal Length", min_val=0, max_val=10, default=1.0)

filtered_df = df[df['petal_length'] > threshold]

table(filtered_df, title="Filtered Iris Data")

fig = px.scatter(filtered_df, x="sepal_length", y="sepal_width", color="species")
plotly(fig)