from preswald import connect, get_df
from preswald import query
from preswald import table, text
from preswald import slider
from preswald import plotly
import plotly.express as px
 
connect()  # Initialize connection to preswald.toml data sources
df = get_df("brain_tumor_dataset")  # Load data
sql = "SELECT * FROM brain_tumor_dataset WHERE Survival_Rate > 50"
filtered_df = query(sql, "brain_tumor_dataset")
text("# My Data Analysis App")
table(filtered_df, title="Filtered Data")
threshold = slider("Threshold", min_val=0, max_val=100, default=50)
table(df[df["Survival_Rate"] > threshold], title="Dynamic Data View")
fig = px.scatter(df, x="Age", y="Survival_Rate", color="Gender")
plotly(fig)
