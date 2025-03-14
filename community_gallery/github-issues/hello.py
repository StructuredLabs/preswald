from preswald import (connect, get_df, slider, selectbox, table, plotly, 
                     text, separator, checkbox, text_input, alert)
from urllib.parse import urlparse
import plotly.express as px
from textblob import TextBlob
from collections import Counter
import pandas as pd
import numpy as np

# ----- Data Loading & Prep -----
connect()
df = get_df("github_issues_sample")

# Preprocessing
def parse_url(url):
    path = urlparse(url).path.split('/')
    return f"{path[1]}/{path[2]}" if len(path) > 3 else "unknown"

df['repo'] = df['issue_url'].apply(parse_url)
df['sentiment'] = df['body'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)

# ----- UI Controls -----
text("# GitHub Issues Explorer")


# ----- Data Filtering -----
filtered = df
# if selected_repo != 'All':
#     filtered = filtered[filtered['repo'] == selected_repo]
   
# if search_term:
#     mask = (filtered['issue_title'].str.contains(search_term, case=False) |
#             filtered['body'].str.contains(search_term, case=False))
#     filtered = filtered[mask]

# filtered = filtered[filtered['sentiment'] >= min_sentiment]

# ----- 1. Language Pie Chart -----
text("## Programming Languages Detected")
langs = ['python', 'js', 'javascript', 'java', 'c++', 'c#', 'php', 'go', 'rust']
filtered['langs'] = (filtered['issue_title'] + filtered['body']).str.lower().apply(
    lambda x: [l for l in langs if l in x])
lang_counts = filtered.explode('langs')['langs'].value_counts()
if not lang_counts.empty:
    plotly(px.pie(lang_counts, names=lang_counts.index, values=lang_counts.values))
else:
    alert("No language keywords found")

# ----- 2. Sentiment & Word Cloud -----
separator()
text("## Text Analysis")

# Sentiment distribution
plotly(px.histogram(filtered, x='sentiment', nbins=20, 
                   title=f"Sentiment Scores (Negative to Positive)"))

# Word cloud alternative
text("### Common Keywords")
all_text = ' '.join(filtered['issue_title'] + ' ' + filtered['body']).lower()
words = [w for w in all_text.split() if len(w) > 3]
word_freq = Counter(words).most_common(50)
filtered_words = [w for w in word_freq if w[1]]

# print(f'Length: {len(filtered_words)}')

print(filtered_words)

if filtered_words:

    df1 = pd.DataFrame(filtered_words, columns=["word", "frequency"])

    # Add a random z-axis value for better 3D visualization
    df1["z"] = np.random.rand(len(df1)) * max(df1["frequency"])

    # Create a 3D scatter plot
    fig = px.scatter_3d(df1, x="word", y="frequency", z="z", 
                        size="frequency", text="word", 
                        title="Word Frequency 3D Scatter Plot")


    df1["z"] = np.random.rand(len(df1))  # Adding a random Z-axis

    fig = px.scatter_3d(df1, x="word", y="frequency", z="z", size="frequency", title="Word Frequency", size_max=50)
    # fig.show()

    # fig = px.treemap(
    #     names=[w[0] for w in filtered_words],
    #     values=[w[1] for w in filtered_words],
    #     title=f"Top Words (Frequency ≥ {word_threshold})"
    # )
    plotly(fig)
else:
    alert("No words meet frequency threshold")

separator()

# selected_repo = selectbox("Choose Repository", ['All'] + sorted(df['repo'].unique()))
min_sentiment = slider("Minimum Sentiment", -1.0, 1.0, 0.1)
row_limit = slider("Rows to Show", 100, 50000, 100)

# ----- 3. Results Table -----
separator()
text(f"## Filtered Issues (Showing {row_limit} rows)")
table_cols = ['issue_title', 'body', 'sentiment']

filtered = filtered[filtered['sentiment'] >= min_sentiment]

table(filtered[table_cols].head(row_limit), 
     title=f"Results matching your filters",
     limit=row_limit)
