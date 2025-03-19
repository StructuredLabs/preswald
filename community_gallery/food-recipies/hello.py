from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald Coding Assesment!")
text("Lets dive into the recipies data and uncover it's delicious secrets 🎉 ~ Nishchal Singi (https://github.com/Nishchal-007)")

connect()
df = get_df('recipies_csv')
df.dropna()
df['total_time'] = df['prep_time (in mins)'] + df['cook_time (in mins)']


# Fig 1: Create a bar chart for Average Cooking Time by Cuisine
avg_time_by_cuisine = df.groupby('cuisine')['total_time'].mean().reset_index()
avg_time_by_cuisine.columns = ['cuisine', 'average_time']
threshold_cuisine = slider("Number of Cuisines", min_val=1, max_val=len(avg_time_by_cuisine), default=5)
filtered_avg_time_by_cuisine = avg_time_by_cuisine.nlargest(threshold_cuisine, 'average_time')
fig_avg_time = px.bar(filtered_avg_time_by_cuisine, x='cuisine', y='average_time',
                       title='Average Cooking Time by Cuisine',
                       labels={'cuisine': 'Cuisine', 'average_time': 'Average Time (minutes)'},
                       color='cuisine', color_discrete_sequence=px.colors.qualitative.Plotly)
fig_avg_time.update_layout(template='plotly_white')
plotly(fig_avg_time)

# Fig 2: Create a pie chart for Recipe Distribution by Course
course_counts = df['course'].value_counts().reset_index()
course_counts.columns = ['course', 'count']
fig_course = px.pie(course_counts, names='course', values='count',
                    title='Recipe Distribution by Course',
                    labels={'course': 'Course Type', 'count': 'Number of Recipes'})
fig_course.update_layout(template='plotly_white')
plotly(fig_course)

# Fig 3: A bar chart for Average Prep & Cook Time by Course
avg_times = df.groupby('course')[['prep_time (in mins)', 'cook_time (in mins)']].mean().reset_index()
avg_times_melted = pd.melt(avg_times, id_vars=['course'], 
                           value_vars=['prep_time (in mins)', 'cook_time (in mins)'],
                           var_name='Time Type', value_name='Average Time')

fig_avg_times = px.bar(avg_times_melted, x='course', y='Average Time', color='Time Type',
                        title='Average Prep & Cook Time by Course',
                        labels={'course': 'Course', 'Average Time': 'Time (minutes)', 'Time Type': 'Time Type'},
                        color_discrete_sequence=px.colors.qualitative.Plotly)
fig_avg_times.update_layout(template='plotly_white')
plotly(fig_avg_times)

# Fig 4: Calculate the counts of each cuisine
cuisine_counts = df['cuisine'].value_counts().reset_index()
cuisine_counts.columns = ['cuisine', 'count']
cuisine_counts['cuisine'] = cuisine_counts['cuisine'].where(cuisine_counts['count'] >= 50, 'Other')
cuisine_counts = cuisine_counts.groupby('cuisine', as_index=False).sum()
fig_cuisine = px.bar(cuisine_counts, x='cuisine', y='count',
                     title='Recipe Distribution by Cuisine',
                     labels={'cuisine': 'Cuisine', 'count': 'Number of Recipes'},
                     color='cuisine', color_discrete_sequence=px.colors.qualitative.Plotly)
fig_cuisine.update_layout(template='plotly_white')
plotly(fig_cuisine)


# Fig 5: a pie chart for Recipe Distribution by Diet Type
diet_counts = df['diet'].value_counts().reset_index()
diet_counts.columns = ['diet', 'count']
fig_diet = px.pie(diet_counts, names='diet', values='count',
                  title='Recipe Distribution by Diet Type',
                  labels={'diet': 'Diet Type', 'count': 'Number of Recipes'},
                  color='diet', color_discrete_sequence=px.colors.qualitative.Plotly,)
fig_diet.update_layout(template='plotly_white')
plotly(fig_diet)

# Fig 6: a bar chart for Ingredient Distribution
threshold = slider("Threshold", min_val=5, max_val=30, default=10)
ingredient_counts = df['ingredients_name'].str.split(',', expand=True).stack().value_counts().reset_index()
ingredient_counts.columns = ['ingredient', 'count']
filtered_df = ingredient_counts[ingredient_counts['count'] > threshold]
top_ingredients = filtered_df.nlargest(threshold, 'count')
fig_ingredient = px.bar(top_ingredients, x='ingredient', y='count',
                        title='Ingredients Distribution',
                        labels={'ingredient': 'Ingredient', 'count': 'Number of Recipes'},
                        color='ingredient', color_discrete_sequence=px.colors.qualitative.Pastel)
fig_ingredient.update_layout(template='plotly_white')
plotly(fig_ingredient)

# table(df)
