from preswald import (connect, get_df, slider, selectbox, table, plotly, 
                     text, separator, checkbox, text_input, alert)
from urllib.parse import urlparse
import plotly.express as px
from collections import Counter
import pandas as pd
import numpy as np

connect()
df = get_df("github_issues_sample")

text("# GitHub Issues Explorer")

def parse_url(url):
    path = urlparse(url).path.split('/')
    return f"{path[1]}/{path[2]}" if len(path) > 3 else "unknown"

df['repo'] = df['issue_url'].apply(parse_url)

positive_words = {"excellent": 3, "great": 2, "good": 1, "amazing": 3, "happy": 2, "love": 3, "like": 1, "wonderful": 3}
negative_words = {"terrible": -3, "bad": -2, "poor": -1, "awful": -3, "sad": -2, "hate": -3, "horrible": -3, "worse": -2}

def sentiment(text):
    words = text.lower().split()
    word_counts = Counter(words)

    sentiment_sum = sum(positive_words.get(word, 0) * word_counts[word] for word in word_counts)
    sentiment_sum += sum(negative_words.get(word, 0) * word_counts[word] for word in word_counts)

    total_words = sum(word_counts.values())
    score = sentiment_sum / (total_words + 1e-5)

    return round(score, 2)

df['sentiment'] = df['body'].apply(sentiment)

filtered = df

# ----- Language Pie Chart -----
text("## Programming Languages Detected")
langs = ['python', 'js', 'javascript', 'java', 'c++', 'c#', 'php', 'go', 'rust']
filtered['langs'] = (filtered['issue_title'] + filtered['body']).str.lower().apply(
    lambda x: [l for l in langs if l in x])
lang_counts = filtered.explode('langs')['langs'].value_counts()
if not lang_counts.empty:
    plotly(px.pie(lang_counts, names=lang_counts.index, values=lang_counts.values))
else:
    alert("No language keywords found")

# ----- Sentiment & Word Cloud -----
separator()
text("## Text Analysis")

# Sentiment distribution
plotly(px.histogram(filtered, x='sentiment', nbins=20, 
                   title=f"Sentiment Scores (Negative to Positive)"))

# Word cloud scatter
text("### Common Keywords")
all_text = ' '.join(filtered['issue_title'] + ' ' + filtered['body']).lower()
words = [w for w in all_text.split() if len(w) > 3]
word_freq = Counter(words).most_common(50)
filtered_words = [w for w in word_freq if w[1]]

# print(filtered_words)

if filtered_words:
    df1 = pd.DataFrame(filtered_words, columns=["word", "frequency"])
    df1["z"] = np.random.rand(len(df1)) * max(df1["frequency"])
    fig = px.scatter_3d(df1, x="word", y="frequency", z="z", size="frequency", text="word", title="Word Frequency 3D Scatter Plot")
    df1["z"] = np.random.rand(len(df1))
    fig = px.scatter_3d(df1, x="word", y="frequency", z="z", size="frequency", title="Word Frequency", size_max=50)
    plotly(fig)
else:
    alert("No words meet frequency threshold")

separator()

min_sentiment = slider("Minimum Sentiment", -1.0, 1.0, 0.1)
row_limit = slider("Rows to Show", 100, 50000, 100)

# ----- Results Table -----
separator()
text(f"## Filtered Issues (Showing {row_limit} rows)")
table_cols = ['issue_title', 'body', 'sentiment']

filtered = filtered[filtered['sentiment'] >= min_sentiment]

table(filtered[table_cols].head(row_limit), 
     title=f"Results matching your filters",
     limit=row_limit)
