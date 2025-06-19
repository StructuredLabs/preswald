from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px
from preswald import connect, get_df, query, table, text, slider, selectbox, plotly
import plotly.express as px

sql = "SELECT * FROM Social_Network_Ads WHERE EstimatedSalary > 50000"
connect()  

df = get_df("Social_Network_Ads")
target = "Purchased"
filtered_df = query(sql, "Social_Network_Ads")
text("# Social Media Purchase Analysis App")
text("# Predicts whether users will purchase an item based on their age, gender, and estimated salary")

col_ops = list(df.columns)
col_ops.remove(target)

col_ops2 = list(df.columns)
col_ops2.remove(target)

choice1 = selectbox(
    label="Choose the first column to show in graph",
    options=list(col_ops),
)


col_ops2.remove(choice1)

choice2 = selectbox(
    label="Choose the second column to show in graph",
    options=list(col_ops2),
)

fig = px.scatter(df, x=choice1, y=choice2, color="Purchased")
plotly(fig)

