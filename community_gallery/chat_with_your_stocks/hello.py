from preswald import text, plotly, connect, get_df, table , query ,button , text_input , selectbox
import pandas as pd
import plotly.express as px
from openai import OpenAI  # Asumiendo que usarás OpenAI para generar las consultas SQL
import logging
import toml


########## We Obtain the api key from secrets.toml #############

secrets=toml.load("./secrets.toml")
openai_api_key = secrets['api_keys']['openai']

openai = OpenAI(
    api_key= openai_api_key
)

text("# 📈 Stock Market Analysis: Amazon vs Tesla")
text("""
Welcome to our interactive stock analysis platform! This powerful template allows you to:
- Analyze any dataset through comprehensive visualizations
- Ask questions in natural language about the data
- Get instant insights powered by AI

Our AI agent at the bottom of the page will translate your questions into SQL queries and provide clear, 
human-readable answers about any aspect of the data you're interested in.
""")

############ connect and read the dataset ############
connect()

#############  CHOOSE WHICH DATASET WE WANT TO ANALYZE?   ############ 
choice = selectbox(
    label="Choose which stock market data you want to explore",
    options=["Amazon Stock", "Tesla Stock"],
    default="Amazon Stock",
    size=2
)
#description="Dive into historical data from two tech giants"

print(f"User selected: {choice}")


if choice == "Amazon Stock":
    file_name = 'amazon_stock_since_1997_to_2025_csv'
elif choice == "Tesla Stock":
    file_name = 'tesla_stock_v2_csv'   
else:
    file_name = 'amazon_stock_since_1997_to_2025_csv'

#tesla_stock_v2_csv
#sample_csv
df = get_df(file_name)

table_name=file_name





def generate_eda(df):
    """
    Performs a comprehensive Exploratory Data Analysis (EDA) for any dataset.

    This function generates a complete EDA report including general information,
    data types analysis, numerical and categorical variable analysis, correlations,
    and key findings.

    Args:
        df (pandas.DataFrame): The input DataFrame to analyze.

    Returns:
        str: A message confirming the EDA completion.

    Example:
        >>> df = pd.read_csv('data.csv')
        >>> generate_eda(df)
        'EDA analysis completed successfully'
    """
    # 1. General Dataset Information
    text("# 📊 Exploratory Data Analysis (EDA)")
    text("## 1. General Information")
    text(f"- Total records: {len(df)}")
    text(f"- Total columns: {len(df.columns)}")
    text(f"- Memory usage: {df.memory_usage().sum() / 1024:.2f} KB")
    
    # Move Data Sample to be the third section
    text("## 2. 👀 Quick Data Preview")
    table(df.head(), title="First 5 records")
    
    # 3. Data Types Analysis (previously section 2)
    text("## 3. 📋 Data Types")
    dtypes_df = pd.DataFrame({
        'Column': df.dtypes.index,
        'Type': df.dtypes.values,
        'Null Values': df.isnull().sum(),
        '% Nulls': (df.isnull().sum() / len(df) * 100).round(2)
    })
    table(dtypes_df, title="Column Information")

    # 4. Numerical Analysis
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) > 0:
        text("## 4. 📈 Numerical Variables Analysis")
        stats_df = df[numeric_cols].describe().round(2)
        table(stats_df, title="Numerical Statistics")
        
        # Distribution visualization
        for col in numeric_cols[:5]:  # Limit to 5 columns to avoid overloading
            fig = px.histogram(df, x=col, title=f'Distribution of {col}')
            plotly(fig)
            
            # Boxplot for outlier detection
            fig = px.box(df, y=col, title=f'Boxplot of {col}')
            plotly(fig)

    # 5. Categorical Analysis
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        text("## 5. 📊 Categorical Variables Analysis")
        for col in categorical_cols:
            value_counts = df[col].value_counts().reset_index()
            value_counts.columns = [col, 'Frequency']
            table(value_counts, title=f"Distribution of {col}")
            
            # Bar chart for categories
            if len(df[col].unique()) <= 20:  # Only if 20 or fewer categories
                fig = px.bar(value_counts, x=col, y='Frequency', 
                           title=f'Distribution of {col}')
                plotly(fig)

    # 6. Correlation Analysis
    if len(numeric_cols) > 1:
        text("## 6. 🔄 Correlation Matrix")
        corr_matrix = df[numeric_cols].corr().round(2)
        fig = px.imshow(corr_matrix,
                       title='Heatmap - Correlations',
                       color_continuous_scale='RdBu')
        plotly(fig)

    # 7. Summary of Findings
    text("## 7. 📝 Summary of Findings")
    text("### Key Points:")
    text(f"- Dataset with {len(df)} rows and {len(df.columns)} columns")
    text(f"- Numerical variables: {len(numeric_cols)}")
    text(f"- Categorical variables: {len(categorical_cols)}")
    
    # Identify columns with null values
    cols_with_nulls = df.columns[df.isnull().any()].tolist()
    if cols_with_nulls:
        text("- Columns with null values: " + ", ".join(cols_with_nulls))
    else:
        text("- No null values found in the dataset")

    return "EDA analysis completed successfully"



def response_the_user_question_with_sql(submit_button, user_question, table_name):
    """
    Processes natural language questions and generates SQL queries to answer them.

    This function takes a user question, converts it to SQL using OpenAI's API,
    executes the query, and provides both the raw results and a natural language
    interpretation.

    Args:
        submit_button (bool): Flag indicating if the form was submitted.
        user_question (str): The natural language question from the user.
        table_name (str): The name of the table to query.

    Returns:
        None: Results are displayed using the text() and table() functions.

    Example:
        >>> response_the_user_question_with_sql(True, "What is the average value?", "sample_table")
    """
    if submit_button:
        if user_question:
            # Show user question
            text(f"**Your question:** {user_question}")
            
            # Convert DataFrame to safe string format
            df_info = f"""
            Available columns: {', '.join(df.columns)}
            Example data:
            {df.head().to_string()}
            """
            
            prompt = f"""
            Given the following database structure:
            {df_info}

            Table: {table_name}
            
            Generate a SQL query to answer this question: {user_question}
            Only return the SQL query, without explanations.

            For example:
            SELECT value FROM {table_name} WHERE item = 'Item A';
            """
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": "You are an expert SQL converter who converts natural language questions into precise SQL queries."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract and clean generated SQL query
            sql_query = response.choices[0].message.content.strip()
            sql_query = sql_query.replace('"', '').replace('`', '').replace('sql', '').strip(';')
            
            # Show generated query
            text("**Generated SQL:**")
            text(f"```sql\n{sql_query}\n```")
            
            try:
                # Execute query
                text("**Query to execute:**")
                text(sql_query)
                text("\n**Target Table:**")
                text(table_name)
                
                # Execute queries and convert results to string
                result = query(sql_query, table_name)

                
                # Show results using table() instead of text()
                text("**Query Results:**")
                table(result)  # Use table() to display DataFrames
                
                
                # Convert result to string for prompt
                result_str = result.to_string() if hasattr(result, 'to_string') else str(result)
                
                # Generate natural language response
                result_prompt = f"""
                Given the following question: {user_question}
                And the following results from the SQL query:
                {result_str}
                
                Provide a clear and concise natural language response that answers the question.
                """
                
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that explains data in a clear and concise manner."},
                        {"role": "user", "content": result_prompt}
                    ]
                )
                
                natural_response = response.choices[0].message.content.strip()
                
                # Show response
                text("**Natural Language Response:**")
                text(natural_response)
                
            except Exception as e:
                text(f"**Error executing query:** {str(e)}")
                import traceback
                text(f"**Error details:**\n```\n{traceback.format_exc()}\n```")
        else:
            text("**Please enter a question to continue.**")

############# Questions #####################

############# English #############
# 1. What is the quantity of products in Item D?
# 2. What is the value of the products in Item A?
# 3. How much do the different items cost?

############### Tesla ##################
# 1. which was the data that the stock is highest price
# 2. Whic was the best day to invest in Tesla

generate_eda(df)
text("# Natural Language Data Query")
text("Ask questions about the dataset and I'll respond with relevant information.")

text(""" ### 📝 Example Questions You Can Ask:

    #### Price Analysis
    - What was the highest stock price ever recorded and on which date?
    - What was the lowest closing price in 2020?
    - Show me the days where the closing price was above $300
    - What's the average closing price for the last 30 days?

    #### Volume Analysis
    - Which day had the highest trading volume?
    - What was the average trading volume in 2021?
    - Show me the top 5 days with highest trading volume
    - List days where volume exceeded 100 million shares

    #### Trading Patterns
    - What days had the biggest price difference between high and low?
    - Show me days where closing price was higher than opening price
    - What was the largest single-day price increase?
    - Find days with unusual trading patterns (high volume + large price swing)

    #### Time-based Analysis
    - How did the stock perform in January 2023?
    - Compare average prices between 2021 and 2022
    - What was the stock's performance in the first quarter of 2022?
    - Show me the highest price for each year

    #### Investment Analysis
    - What were the best days to buy (lowest prices)?
    - What were the best days to sell (highest prices)?
    - Calculate the monthly average closing prices
    - Show days with significant price drops (>10%)

    """)

user_question = text_input(label="What would you like to know about the data?", 
                          placeholder="For example: What is the value of Item D?")


submit_button = button("Query")

logging.info(f"submit button  {submit_button}")

if submit_button :
    response_the_user_question_with_sql(submit_button, user_question , table_name)
print("cual es el valor del item D")


