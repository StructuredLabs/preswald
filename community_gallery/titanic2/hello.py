from preswald import connect, text, plotly, slider, get_df, table, separator, selectbox
import pandas as pd
import plotly.express as px

connect()

text("# Welcome to The Titanic Dataset Visualizer!", size=0.7)
text("Lance Garrick Soares", size=0.3)

my_df = get_df('titanic2')
my_df['Survived'] = my_df['Survived'].replace({0: 'Died', 1: 'Survived'})
my_df['Sex'] = my_df['Sex'].replace({'male': 'M', 'female': 'F'})
my_df['Fare'] = my_df['Fare'].round(2)
my_df['Name'] = my_df['Name'].apply(lambda x: x[:20] + '...' if len(x) > 20 else x)

table(my_df, limit=10, title="Titanic Dataset")

text("## % Survived by:", size=0.25)
choice = selectbox(
    label="Parameter",
    options=["Sex", "Age", "Ticket Class", "Port of Embarkation"],
    size=0.75
)

# Use the selected option
if choice == "Sex":
    sex = selectbox(
        label="Choose Sex",
        options=["Male", "Female"],
        size=0.25
    )
    if sex == "Male":
        df_sex = my_df[my_df['Sex'] == 'M']
    else:
        df_sex = my_df[my_df['Sex'] == 'F']
    
    survival_counts = df_sex['Survived'].value_counts().replace({0: 'Died', 1: 'Survived'})

    fig = px.pie(
        names=survival_counts.index, 
        values=survival_counts.values, 
        color=survival_counts.index,
        color_discrete_map={"Survived": "green", "Died": "red"}
    )
    plotly(fig, size=0.75)

elif choice == "Age":
    value = slider(
        label="Select Age Range",
        min_val=1,
        max_val=100,
        step=10,
        default=20,
        size=0.25
    )
    df_age = my_df[my_df['Age'] <= value]
    
    survival_counts = df_age['Survived'].value_counts().replace({0: 'Died', 1: 'Survived'})

    fig = px.pie(
        names=survival_counts.index, 
        values=survival_counts.values, 
        color=survival_counts.index,
        color_discrete_map={"Survived": "green", "Died": "red"}
    )
    plotly(fig, size=0.75)

elif choice=="Ticket Class":
    tclass = selectbox(
        label="Choose Ticket Class",
        options=["1st Class", "2nd Class", "3rd Class"],
        size=0.25
    )
    if tclass == "1st Class":
        df_tclass = my_df[my_df['Pclass'] == 1]
    elif tclass == "2nd Class":
        df_tclass = my_df[my_df['Pclass'] == 2]
    else:
        df_tclass = my_df[my_df['Pclass'] == 3]
    
    survival_counts = df_tclass['Survived'].value_counts().replace({0: 'Died', 1: 'Survived'})

    fig = px.pie(
        names=survival_counts.index, 
        values=survival_counts.values, 
        color=survival_counts.index,
        color_discrete_map={"Survived": "green", "Died": "red"}
    )
    plotly(fig, size=0.75)

elif choice=="Port of Embarkation":
    port = selectbox(
        label="Choose Port",
        options=["Cherbourg", "Queenstown", "Southampton"],
        size=0.25
    )

    if port == "Cherbourg":
        df_port = my_df[my_df['Embarked'] == 'C']
    elif port == "Queenstown":
        df_port = my_df[my_df['Embarked'] == 'Q']
    else:
        df_port = my_df[my_df['Embarked'] == 'S']

    survival_counts = df_port['Survived'].value_counts().replace({0: 'Died', 1: 'Survived'})
    fig = px.pie(
        names=survival_counts.index, 
        values=survival_counts.values, 
        color=survival_counts.index,
        color_discrete_map={"Survived": "green", "Died": "red"}
    )
    plotly(fig, size=0.75)


df_encoded = my_df.copy()
df_encoded['Sex'] = df_encoded['Sex'].map({'M': 0, 'F': 1})
df_encoded['Survived'] = df_encoded['Survived'].map({'Died': 0, 'Survived': 1})  # Encoding survived (0 = No, 1 = Yes)
df_encoded = pd.get_dummies(df_encoded, columns=['Embarked']) 
df_encoded = df_encoded.drop(['Name', 'Ticket', 'Cabin', 'PassengerId'], axis=1)

corr_matrix = df_encoded.corr()

text("## Correlation Matrix")
fig = px.imshow(corr_matrix, color_continuous_scale='RdBu')
plotly(fig)

text("## Relational Plots:", size=0.3) 
text(" Age VS Fare by", size= 0.2)


param = selectbox(
    label="Choose Relaitonship",
    options=["Sex", "Port of Embarkation", "Survived"],
    size=0.5
)

fig = px.scatter(
    my_df, 
    x="Age", 
    y="Fare", 
    color= param if param == "Sex" else "Survived" if param == "Survived" else "Embarked", 
    symbol= param if param == "Sex" else "Survived" if param == "Survived" else "Embarked", 
    labels={"Age": "Age", "Fare": "Fare"},
)
fig.update_layout(
    xaxis_title="Age",
    yaxis_title="Fare",
    template='plotly_white'
)
plotly(fig, size=1)