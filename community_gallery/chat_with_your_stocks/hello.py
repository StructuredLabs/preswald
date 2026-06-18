from preswald import text, plotly, connect, get_df, table , query ,button , text_input , selectbox
import pandas as pd
import plotly.express as px
from openai import OpenAI  # Asumiendo que usarás OpenAI para generar las consultas SQL
import logging
import toml
import statsmodels


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
            # Histogram with KDE overlay
            fig = px.histogram(df, x=col, title=f'Distribution of {col}', 
                               histnorm='probability density',
                               marginal='box')
            plotly(fig)
            
            # Boxplot for outlier detection
            fig = px.box(df, y=col, title=f'Boxplot of {col}')
            plotly(fig)
            
            # Time series analysis if 'Date' column exists
            if 'Date' in df.columns:
                # Convert 'Date' to datetime if it isn't already
                if not pd.api.types.is_datetime64_any_dtype(df['Date']):
                    try:
                        date_series = pd.to_datetime(df['Date'])
                        # Line chart showing trend over time
                        fig = px.line(df, x='Date', y=col, title=f'{col} Over Time')
                        fig.update_xaxes(rangeslider_visible=True)
                        plotly(fig)
                        
                        # Add moving average line (30-day window)
                        if len(df) > 30:
                            ma_df = df.copy()
                            ma_df[f'{col}_MA30'] = ma_df[col].rolling(window=30).mean()
                            fig = px.line(ma_df, x='Date', y=[col, f'{col}_MA30'], 
                                        title=f'{col} with 30-day Moving Average')
                            fig.update_layout(legend_title_text='Metric')
                            plotly(fig)
                    except:
                        # If date conversion fails, skip time series analysis
                        pass
        
        # Scatter Matrix for key numerical variables (limited to prevent overload)
        if len(numeric_cols) >= 2:
            key_cols = numeric_cols[:4]  # Limit to 4 columns for scatter matrix
            fig = px.scatter_matrix(df, dimensions=key_cols, 
                                   title='Scatter Matrix of Key Numerical Variables')
            plotly(fig)
            
            # 3D scatter plot if we have at least 3 numerical columns
            if len(numeric_cols) >= 3:
                fig = px.scatter_3d(df, x=numeric_cols[0], y=numeric_cols[1], z=numeric_cols[2],
                                   title='3D Relationship Between Key Variables',
                                   opacity=0.7)
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
                
                # Pie chart as alternative visualization
                fig = px.pie(value_counts, names=col, values='Frequency', 
                            title=f'Proportion of {col} Categories')
                plotly(fig)
                
                # If we have numerical columns, create box plots by category
                if len(numeric_cols) > 0:
                    for num_col in numeric_cols[:3]:  # Limit to 3 numerical columns
                        fig = px.box(df, x=col, y=num_col, 
                                   title=f'{num_col} Distribution by {col}')
                plotly(fig)

    # 6. Correlation Analysis
    if len(numeric_cols) > 1:
        text("## 6. 🔄 Correlation Matrix")
        corr_matrix = df[numeric_cols].corr().round(2)
        
        # Enhanced correlation heatmap
        fig = px.imshow(corr_matrix,
                       title='Heatmap - Correlations',
                       color_continuous_scale='RdBu_r',
                       text_auto=True)
        fig.update_layout(height=600, width=700)
        plotly(fig)

        # Identify and visualize the most correlated pairs
        corr_pairs = corr_matrix.unstack().sort_values(ascending=False)
        # Remove self-correlations (which are always 1.0)
        corr_pairs = corr_pairs[corr_pairs < 1.0]
        
        if not corr_pairs.empty:
            # Get top 5 correlations
            top_corrs = corr_pairs.head(5)
            text("### Top Correlations")
            for idx, corr in top_corrs.items():
                var1, var2 = idx
                text(f"- {var1} & {var2}: {corr:.2f}")
                # Create scatter plot for top correlated pairs
                fig = px.scatter(df, x=var1, y=var2, 
                                title=f'Correlation: {var1} vs {var2} (r={corr:.2f})',
                                trendline='ols')  # Add trend line
                plotly(fig)
        
    # 7. Time Series Analysis (if applicable)
    if 'Date' in df.columns:
        text("## 7. 📅 Time Series Analysis")
        # Convert date if needed
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            try:
                df['Date'] = pd.to_datetime(df['Date'])
                
                # Group data by year and month to see trends
                df['Year'] = df['Date'].dt.year
                df['Month'] = df['Date'].dt.month
                
                # Monthly averages of key metrics
                if len(numeric_cols) > 0:
                    for col in numeric_cols[:3]:  # Limit to 3 most important numerical columns
                        monthly_avg = df.groupby(['Year', 'Month'])[col].mean().reset_index()
                        monthly_avg['YearMonth'] = monthly_avg['Year'].astype(str) + '-' + monthly_avg['Month'].astype(str)
                        
                        fig = px.line(monthly_avg, x='YearMonth', y=col, 
                                     title=f'Monthly Average of {col}',
                                     labels={'YearMonth': 'Year-Month', col: f'Avg {col}'})
                        fig.update_xaxes(tickangle=45)
                        plotly(fig)
                
                # Seasonal decomposition visualization for key metrics if we have enough data
                if len(df) > 365:  # Need at least a year of data
                    from statsmodels.tsa.seasonal import seasonal_decompose
                    import numpy as np
                    
                    try:
                        for col in numeric_cols[:2]:  # Limit to 2 columns
                            # Set Date as index for decomposition
                            ts_df = df.set_index('Date')[[col]].resample('D').mean().fillna(method='ffill')
                            
                            # Calculate trend, seasonality, and residuals
                            decomposition = seasonal_decompose(ts_df, model='multiplicative', period=30)
                            
                            # Create plots for decomposition
                            trend = decomposition.trend
                            seasonal = decomposition.seasonal
                            residual = decomposition.resid
                            
                            # Plot components
                            fig = px.line(x=trend.index, y=trend.values, title=f'Trend Component of {col}')
                            fig.update_layout(xaxis_title='Date', yaxis_title='Trend')
                            plotly(fig)
                            
                            fig = px.line(x=seasonal.index, y=seasonal.values, title=f'Seasonal Component of {col}')
                            fig.update_layout(xaxis_title='Date', yaxis_title='Seasonality')
                            plotly(fig)
                            
                            fig = px.line(x=residual.index, y=residual.values, title=f'Residual Component of {col}')
                            fig.update_layout(xaxis_title='Date', yaxis_title='Residuals')
                            plotly(fig)
                    except:
                        text("⚠️ Could not perform seasonal decomposition. This often requires regular time series data.")
            except:
                text("⚠️ Failed to process date information for time series analysis.")

    # 8. Summary of Findings
    text("## 8. 📝 Summary of Findings")
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
        
    # Add statistics about key variables
    if len(numeric_cols) > 0:
        text("### Key Statistics:")
        for col in numeric_cols[:3]:  # Limit to 3 columns
            text(f"- {col}: Mean = {df[col].mean():.2f}, Min = {df[col].min():.2f}, Max = {df[col].max():.2f}")
            
    # Auto-detect potential outliers
    text("### Potential Outliers:")
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outlier_count = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
        if outlier_count > 0:
            text(f"- {col}: {outlier_count} potential outliers detected")

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

def create_temporal_overview(df):
    """
    Creates a comprehensive temporal visualization showing multiple variables together.
    
    Args:
        df (pandas.DataFrame): DataFrame with time series data
    """
    text("## 📊 Temporal Overview")
    text("This visualization shows key metrics together to help understand their relationships over time.")
    
    # Verificar si existe la columna Date
    if 'Date' not in df.columns:
        text("⚠️ No date column found in the dataset for temporal visualization.")
        return
    
    # Convertir a datetime si no lo es ya
    try:
        df['Date'] = pd.to_datetime(df['Date'])
    except:
        text("⚠️ Could not convert the Date column to datetime.")
        return
    
    # Seleccionar las columnas numéricas más importantes (excluyendo Volume que tiene escala diferente)
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    price_cols = [col for col in numeric_cols if col in ['Open', 'High', 'Low', 'Close'] and col != 'Volume']
    
    if len(price_cols) > 0:
        # Crear un subconjunto de datos para no sobrecargar el gráfico
        if len(df) > 1000:
            # Usar muestreo para grandes datasets
            sampled_df = df.sort_values('Date').reset_index(drop=True)
            sample_size = min(1000, len(df))
            sample_indices = sorted(pd.Series(range(len(df))).sample(sample_size).tolist())
            sampled_df = df.iloc[sample_indices].sort_values('Date').reset_index(drop=True)
        else:
            sampled_df = df.sort_values('Date').reset_index(drop=True)
        
        # Crear gráfico de líneas para variables de precio
        fig = px.line(sampled_df, x='Date', y=price_cols, 
                     title='Stock Price Metrics Over Time',
                     labels={'value': 'Price', 'variable': 'Metric'})
        
        # Mejorar diseño del gráfico
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode="x unified",
            plot_bgcolor='rgba(240, 240, 240, 0.8)',  # Fondo suave
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(200, 200, 200, 0.3)',
                rangeslider_visible=True
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(200, 200, 200, 0.3)',
                title="Price ($)"
            )
        )
        plotly(fig)
        
        # Mostrar volumen como gráfico de barras en un gráfico separado si existe
        if 'Volume' in df.columns:
            fig = px.bar(sampled_df, x='Date', y='Volume', 
                       title='Trading Volume Over Time',
                       color_discrete_sequence=['rgba(76, 114, 176, 0.7)'])
            
            fig.update_layout(
                plot_bgcolor='rgba(240, 240, 240, 0.8)',
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    rangeslider_visible=True
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    title="Volume"
                )
            )
            plotly(fig)
            
        # Crear gráfico de velas si tenemos Open, High, Low y Close
        if all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
            # Limitar a los últimos 90 días para no sobrecargar el gráfico
            last_90_days = sampled_df.sort_values('Date').tail(90)
            
            import plotly.graph_objects as go
            fig = go.Figure(data=[go.Candlestick(
                x=last_90_days['Date'],
                open=last_90_days['Open'],
                high=last_90_days['High'],
                low=last_90_days['Low'],
                close=last_90_days['Close'],
                name='Price'
            )])
            
            fig.update_layout(
                title='Candlestick Chart (Last 90 Days)',
                xaxis_title='Date',
                yaxis_title='Price',
                xaxis_rangeslider_visible=True,
                plot_bgcolor='rgba(240, 240, 240, 0.8)',
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200, 200, 200, 0.3)',
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200, 200, 200, 0.3)',
                )
            )
            plotly(fig)
    else:
        text("⚠️ No suitable price columns found for temporal visualization.")

# Modificar la parte de generación del EDA para incluir la vista temporal
generate_eda(df)

# Agregar el gráfico temporal después del EDA
create_temporal_overview(df)

text("# Natural Language Data Query")
text("Ask questions about the dataset and I'll respond with relevant information.")

# Mejorar la sección de preguntas de ejemplo con un diseño más visual


text(""" ## 📝 Example Questions You Can Ask""")

text("- What was the highest stock price ever recorded and on which date?")
text("- What was the lowest closing price in 2023?")
text("- what was the best day to buy this stock")
text("- What's the average closing price for the last 90 days?")



user_question = text_input(label="What would you like to know about the data?", 
                          placeholder="For example: What was the highest stock price ever recorded?")

submit_button = button("Query")

logging.info(f"submit button  {submit_button}")

if submit_button :
    response_the_user_question_with_sql(submit_button, user_question , table_name)
print("cual es el valor del item D")


