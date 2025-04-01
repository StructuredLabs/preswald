from preswald import sklearn_predictor, slider

features = {
    "sepal_length": slider("Sepal Length", 4.0, 8.0, default=5.1, size=0.5),
    "sepal_width": slider("Sepal Width", 2.0, 4.5, default=3.5, size=0.5),
    "petal_length": slider("Petal Length", 1.0, 7.0, default=1.4, size=0.5),
    "petal_width": slider("Petal Width", 0.1, 2.5, default=0.2, size=0.5),
}

# ✅ You MUST actually call it
prediction = sklearn_predictor(
    model_path="models/iris_model.pkl",
    input_features=features,
    output_label="Predicted Species"
)
