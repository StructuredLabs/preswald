from preswald import text, selectbox, slider, plotly, connect, get_df
import pandas as pd
import umap
import plotly.express as px
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF, PCA

text("# Topic Modeling App")
text("## Select Methods for each Stage")

feature_extraction_methods = ["TF-IDF", "CountVectorizer"]
topic_modeling_methods = ["NMF", "LDA"]
dim_reduction_methods = ["UMAP", "PCA"]

connect()
df = get_df('TopicModeling')

selectbox_size = 1.0 / 3
selected_feature_extraction = selectbox("Feature Extraction Method", options=feature_extraction_methods, default="TF-IDF", size=selectbox_size)
selected_topic_modeling = selectbox("Topic Modeling Method", options=topic_modeling_methods, default="NMF", size=selectbox_size)
selected_dim_reduction = selectbox("Dimensionality Reduction Method", options=dim_reduction_methods, default="UMAP", size=selectbox_size)

param_options = {
    "TF-IDF": {"max_features": (1000, 10000, 1000), "ngram_range": ["(1,1)", "(1,2)", "(1,3)"]},
    "CountVectorizer": {"max_features": (1000, 10000, 1000), "ngram_range": ["(1,1)", "(1,2)", "(1,3)"]},
    "NMF": {"nmf_n_components": (2, 20, 2), "alpha": (0.0, 0.5, 0.05)},
    "LDA": {"lda_n_components": (2, 20, 2), "learning_method": ["batch", "online"]},
    "UMAP": {"n_neighbors": (5, 50, 5), "min_dist": (0.0, 1.0, 0.1)},
    "PCA": {"pca_n_components": (2, 20, 2)}
}

label_map = {
    "max_features" : "Max Features",
    "ngram_range" : "N-grams Range",
    "nmf_n_components": "N-components",
    "alpha" : "Alpha",
    "lda_n_components" : "N-components",
    "learning_method" : "Learning Method",
    "n_neighbors" : "Number of Neighbors",
    "min_dist" : "Minimum Distance",
    "pca_n_components" : "N-components"
}

text("## Adjust Parameters")

selected_params = {}
for method in [selected_feature_extraction, selected_topic_modeling, selected_dim_reduction]:
    if method in param_options:
        text(f"### Parameters for {method}")
        for param, values in param_options[method].items():
            if isinstance(values, tuple):  # Slider (min, max, default)
                selected_params[param] = slider(label=label_map[param], min_val=values[0], max_val=values[1], step=values[2], size=0.5)
            else:  # Dropdown (Ensure string format for tuple-like values)
                selected_params[param] = selectbox(label=label_map[param], options=values, default=str(values[0]), size=0.5)

def get_vectorizer(method, max_features):
    if method == "count":
        return CountVectorizer(stop_words="english", max_features=max_features)
    return TfidfVectorizer(stop_words="english", max_features=max_features)

vectorizer = get_vectorizer(selected_feature_extraction.lower(), selected_params.get("max_features", 5000))
tfidf_matrix = vectorizer.fit_transform(df["ABSTRACT"])

def get_topic_model(method, num_topics):
    if method == "LDA":
        return LatentDirichletAllocation(n_components=num_topics, random_state=42)
    return NMF(n_components=num_topics, random_state=42)

topic_model = get_topic_model(selected_topic_modeling, selected_params.get("nmf_n_components", 10))
topic_matrix = topic_model.fit_transform(tfidf_matrix)
df["topic"] = topic_matrix.argmax(axis=1)

def get_topic_keywords(model, feature_names, num_words=5):
    topic_labels = {}
    for topic_idx, topic in enumerate(model.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-num_words - 1:-1]]
        topic_labels[topic_idx] = " | ".join(top_words)
    return topic_labels

feature_names = vectorizer.get_feature_names_out()
topic_labels = get_topic_keywords(topic_model, feature_names)
df["topic_label"] = df["topic"].map(topic_labels)

def get_dim_reduction(method, n_components):
    if method == "PCA":
        return PCA(n_components=n_components, random_state=42)
    return umap.UMAP(n_components=n_components, random_state=42)

dim_model = get_dim_reduction(selected_dim_reduction, selected_params.get("pca_n_components", 2))
dim_embeddings = dim_model.fit_transform(topic_matrix)
df["x"], df["y"] = dim_embeddings[:, 0], dim_embeddings[:, 1]

def wrap_text(text, width=80):
    return '<br>'.join(text[i:i+width] for i in range(0, len(text), width))

df["article_abstract"] = df["ABSTRACT"].apply(lambda x: wrap_text(x, width=80))

fig = px.scatter(
    df, 
    x="x", 
    y="y", 
    color=df["topic_label"],
    hover_data={"article_abstract": True, "x": False, "y": False},
    title="Interactive Topic Modeling Visualization",
    labels={"topic_label": "Topic"},
    opacity=0.7,
    color_discrete_sequence=px.colors.qualitative.Set1
)
fig.update_layout(
    width=900, 
    height=600, 
    legend_title="Topics"
)
plotly(fig)


bar_data = df["topic_label"].value_counts().reset_index()
bar_data.columns = ["Topic", "Document Count"]
fig_bar = px.bar(
    bar_data,
    x="Topic",
    y="Document Count",
    labels={"Topic": "Topic", "Document Count": "Document Count"},
    title="Topic Distribution",
    color="Topic",
    color_discrete_sequence=px.colors.qualitative.Set1
)
plotly(fig_bar)

