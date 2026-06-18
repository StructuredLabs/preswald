from preswald import text, plotly, connect, get_df, table
import plotly.graph_objects as go
from preswald import query
from preswald import table, text
from preswald import slider
from preswald import plotly
import numpy as np

def create_bar_chart(df):
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=df["Company Name"],
        y=df["Mean Hourly Gap"],
        name="Mean Hourly Gap"
    ))
    fig1.add_trace(go.Bar(
        x=df["Company Name"],
        y=df["Median Hourly Gap"],
        name="Median Hourly Gap"
    ))
    fig1.add_trace(go.Bar(
        x=df["Company Name"],
        y=df["Mean Bonus Gap"],
        name="Mean Bonus Gap"
    ))
    fig1.add_trace(go.Bar(
        x=df["Company Name"],
        y=df["Median Bonus Gap"],
        name="Median Bonus Gap"
    ))

    fig1.update_layout(
        barmode='group',
        title="Comparison of Mean/Median Hourly & Bonus Gaps by Company",
        xaxis_title="Company Name",
        yaxis_title="Percentage Gap",
        legend_title="Measure",
        xaxis=dict(tickangle=45, automargin=True)
    )

    return fig1



def create_scatter_plot(df):
    max_female = df["Percentage Employees Female"].max()
    if max_female <= 0 or np.isnan(max_female):
        max_female = 1  

    sizeref_value = 2.0 * max_female / (40.0 ** 2)

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=df["Mean Hourly Gap"],
        y=df["Mean Bonus Gap"],
        mode='markers+text',
        text=df["Company Name"],
        textposition='top center',
        marker=dict(
            size=df["Percentage Employees Female"],
            color=df["Percentage Employees Female"],
            showscale=True,
            colorbar=dict(
                title="% Female Employees",   
                x=1.15,                       
                xanchor='left',
            ),
            sizemode='area',
            sizeref=sizeref_value,
            sizemin=5
        )
    ))

    fig2.update_layout(
        title="Mean Hourly Gap vs. Mean Bonus Gap (Bubble Size & Color = % Female Employees)",
        xaxis_title="Mean Hourly Gap (Column Name)",
        yaxis_title="Mean Bonus Gap (Row Name)",
        margin=dict(r=150, l=100, b=100)
    )

    return fig2


# Load the CSV
connect() # load in all sources, which by default is the sample_csv
# df = get_df('irish_pay_gap')
sql = 'SELECT * FROM irish_pay_gap WHERE "Report Year" > 2022'
filtered_df = query(sql, "irish_pay_gap")
filtered_df["non_null_count"] = filtered_df.notna().sum(axis=1)
df_sorted = filtered_df.sort_values("non_null_count", ascending=False)
df = df_sorted.head(20)

text("# Ireland Gender Pay Gap Analysis")
text("### Filtered Data (Report Year > 2022)")
threshold = slider("Median Hourly Gap Threshold", min_val=0, max_val=30, default=0)
table(df[df["Median Hourly Gap"] > threshold], title="Dynamic Data View")

fig1 = create_bar_chart(df)
plotly(fig1)

fig2 = create_scatter_plot(df)
plotly(fig2)