from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import joblib
import pandas as pd

# Load the dataset
iris = load_iris()
X = iris.data
y = iris.target
target_names = iris.target_names  # ['setosa', 'versicolor', 'virginica']

# Optional: Map target to string labels
y_named = [target_names[i] for i in y]

# Train a model
clf = RandomForestClassifier()
clf.fit(X, y_named)

# Save the model
joblib.dump(clf, "models/iris_model.pkl")
print("✅ Model saved as models/iris_model.pkl")
