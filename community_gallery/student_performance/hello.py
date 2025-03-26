# Import necessary modules from Preswald and Plotly
from preswald import text, plotly, connect, get_df, table, slider
import plotly.figure_factory as ff

# -------------------------------
# Title and Dataset Description
# -------------------------------

text("# Student Performance Dataset")

text("""
This dataset analyzes student achievement in secondary education at two Portuguese schools. 
It includes attributes related to **student grades, demographics, social factors, and school-related features**. 
The data was collected using school reports and questionnaires and covers performance in **Mathematics**.

In the study by **Cortez and Silva (2008)**, the dataset was used for binary classification, five-level classification, and regression tasks. 
For more details, refer to the official dataset repository:  
[UCI Student Performance Dataset](https://archive.ics.uci.edu/dataset/320/student+performance)
""")

# -------------------------------
# Connect to Dataset
# -------------------------------

connect()
df = get_df('student')

# Filter dataset to include only students from urban areas ('U')
df = df[df['address'] == 'U']

# -------------------------------
# Interactive Table: Urban Students with High Final Grades
# -------------------------------

text("## Interactive Table: Urban Students with High Final Grades")

# User-defined threshold for final year grades (G3) using a slider
threshold = slider("Min Final Year Grade", min_val=0, max_val=20)

# Display a table of students in urban areas whose final grade (G3) is above the threshold
table(
    df[df["G3"] > threshold].head(10), 
    title="Urban Students with Final Grade Above Threshold"
)

# -------------------------------
# Distribution Plot: Final Year Grades by Higher Education Aspirations
# -------------------------------

text("## Distribution of Final Year Grades by Higher Education Aspirations")
text("""
This plot visualizes the distribution of **final year grades (`G3`)** based on students' aspirations to pursue higher education.

### **Key Observations**  
- Students who plan to continue higher education tend to have **higher final year grades**.  
- **All students with final grades above 13 have aspirations for higher education**.  
This suggests a strong correlation between academic performance and further educational ambitions.
""")

# Labels for the groups: students who do not want vs. do want to continue higher education
group_labels = ["Not Pursuing Higher Education", "Wants Higher Education"]

# Extract G3 scores for both groups
data = [
    df[df['higher'] == 0]['G3'],  # Students not planning for higher education
    df[df['higher'] == 1]['G3']   # Students planning for higher education
]

# Create the KDE distribution plot (smoothed density curve)
fig = ff.create_distplot(
    data, 
    group_labels=group_labels, 
    colors=['#1f77b4', '#ff7f0e'],  # Blue for 'No Higher', Orange for 'Higher'
    show_hist=False,  # Hide histogram bars for a cleaner density plot
    show_rug=False    # Hide rug plot (individual data points)
)

# Fill the area under the KDE curves to enhance visualization
fig.update_traces(fill='tozeroy')

# Display the plot
plotly(fig)