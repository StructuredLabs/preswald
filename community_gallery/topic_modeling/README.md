# Topic Modeling

### Dataset Source
Kaggle: https://www.kaggle.com/datasets/abisheksudarshan/topic-modeling-for-research-articles
(Used only subset of dataset)

### App Details
This app performs interactive topic modeling on research abstracts, allowing users to:

* Select feature extraction methods (TF-IDF or CountVectorizer).
* Choose topic modeling algorithms (NMF or LDA).
* Apply dimensionality reduction (UMAP or PCA) to visualize topic clusters.
* Explore an interactive scatter plot of topics based on selected parameters.
* View a bar chart showing the distribution of documents across different topics.
* Adjust parameters dynamically, such as max_features, n_components, and more.


## Run App
- Install preswald:
```
pip install preswald
```

- Move into the topic-modeling directory:
```
cd preswald/community_gallery/topic_modeling/
```

- Create preswald project
```
preswald init my_app
```

- Move the hello.py and data from topic_modeling to my_app
- Update preswald.toml with dataset file name (TopicModeling.csv)

- Run the app:
```
preswald run
```