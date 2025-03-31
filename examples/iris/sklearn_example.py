from preswald import sklearn_predictor, slider


# Rest of your existing code...
features = {
    "sepal_length": slider("Sepal Length", 4.0, 8.0, default=5.1, size=0.5),
    "sepal_width": slider("Sepal Width", 2.0, 4.5, default=3.5, size=0.5),
    "petal_length": slider("Petal Length", 1.0, 7.0, default=1.4, size=0.5),
    "petal_width": slider("Petal Width", 0.1, 2.5, default=0.2, size=0.5),
}
class_mapping = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]

prediction = sklearn_predictor(
    model_path="models/iris_model.pkl",
    input_features=features,
    class_mapping=class_mapping,
    output_label="Predicted Species",
    size=1.0,
    show_proba=True,
)
