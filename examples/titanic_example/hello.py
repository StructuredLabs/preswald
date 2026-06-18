from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px


connect()


df = get_df("titanic")
print("Before dropping:", df.columns)

# Remove all columns starting with "zero"
df = df.drop(columns=[col for col in df.columns if col.startswith("zero")], errors="ignore")

print("After dropping:", df.columns)



sql = "SELECT * FROM titanic WHERE Age > 30"
filtered_df = query(sql, "titanic")


text("# Titanic Data Analysis App")


table(filtered_df, title="Passengers Older than 30")



threshold = slider("Age Threshold", min_val=0, max_val=80, default=30)
table(df[df["Age"] > threshold], title="Filtered by Age")

df.rename(columns={"2urvived": "Survived"}, inplace=True)


fig = px.histogram(df, x="Pclass", color="Survived", barmode="group", title="Survival by Passenger Class")
plotly(fig)






