from funflow import GridMap, Model, Template, Tag, NoTagFilter, ValueTagFilter, Layer
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import pandas as pd
import networkx as nx

# 1. Realistic Data Science Pipeline with GridMap
# This example demonstrates how to use separate layers for different datasets
# and model types, and how to use tags to create variations of the pipeline
# (e.g., training on raw vs. normalised data).

def load_iris_data():
    print(f"  [Loader] Loading Iris dataset...")
    data = datasets.load_iris()
    return data.data, data.target

def load_wine_data():
    print(f"  [Loader] Loading Wine dataset...")
    data = datasets.load_wine()
    return data.data, data.target

def preprocess_data(data_tuple):
    X, y = data_tuple
    print(f"  [Preprocessor] Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, y

def split_data(data_tuple):
    X, y = data_tuple
    print(f"  [Splitter] Splitting into train/test...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42)
    return (X_train, y_train), (X_test, y_test)

def train_random_forest(train_tuple):
    X_train, y_train = train_tuple
    print(f"  [Trainer] Training RandomForest...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

def train_logistic_regression(train_tuple):
    X_train, y_train = train_tuple
    print(f"  [Trainer] Training LogisticRegression...")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, test_tuple):
    X_test, y_test = test_tuple
    print(f"  [Evaluator] Evaluating model...")
    accuracy = model.score(X_test, y_test)
    return accuracy

def summarize_results(**accuracies):
    print("\n" + "="*50)
    print("             PIPELINE SUMMARY")
    print("="*50)
    
    data = []
    for key, acc in accuracies.items():
        # key format: "accuracy, dataset: iris, model_type: random_forest, processing: raw"
        tags_str = key.split(",", 1)[1] if "," in key else ""
        tags = {t.split(":")[0].strip(): t.split(":")[1].strip() for t in tags_str.split(",") if ":" in t}
        tags['accuracy'] = acc
        data.append(tags)
    
    df = pd.DataFrame(data)
    if not df.empty:
        # Reorder columns for better display
        cols = ['dataset', 'processing', 'model_type', 'accuracy']
        df = df[cols].sort_values(by=['dataset', 'processing', 'accuracy'], ascending=[True, True, False])
        
        print("\nAll Results:")
        print(df.to_string(index=False))
        
        print("\nBest Model per Dataset & Processing Variant:")
        best_models = df.loc[df.groupby(['dataset', 'processing'])['accuracy'].idxmax()]
        print(best_models.to_string(index=False))
    else:
        print("  No results found.")
    
    print("="*50 + "\n")
    return "Summary Generated"

# 2. Define Layers using GridMap

# Loaders: Create two separate loaders for different datasets
# We tag them with 'dataset' and also 'processing:raw'
iris_loader = GridMap(
    load_iris_data,
    inputs=[], 
    outputs=[Template("data", tags=[Tag("dataset", "iris"), Tag("processing", "raw")])],
    name="IrisLoader"
)

wine_loader = GridMap(
    load_wine_data,
    inputs=[],
    outputs=[Template("data", tags=[Tag("dataset", "wine"), Tag("processing", "raw")])],
    name="WineLoader"
)

# Preprocessor: Only processes data tagged with 'processing:raw'
# It produces 'processed_data' tagged with 'processing:normalised'
preprocessor = GridMap(
    preprocess_data,
    inputs=[Template("data", filters=[ValueTagFilter("processing", "raw")])],
    outputs=[Template("data", tags=[Tag("processing", "normalised")])],
    name="Preprocessor"
)

# Splitter: Handles the 'normalised' path
splitter = GridMap(
    split_data,
    inputs=[Template("data")],
    outputs=[
        Template("train_data"),
        Template("test_data")
    ],
    name="Splitter"
)


# Trainers: Separate trainers for different model types
# They automatically join with train_data based on matching 'dataset' and 'processing' tags
rf_trainer = GridMap(
    train_random_forest,
    inputs=[Template("train_data")],
    outputs=[Template("model", tags=[Tag("model_type", "random_forest")])],
    name="RFTrainer"
)

lr_trainer = GridMap(
    train_logistic_regression,
    inputs=[Template("train_data")],
    outputs=[Template("model", tags=[Tag("model_type", "logistic_regression")])],
    name="LRTrainer"
)

# Evaluator: Joins models with their corresponding test data
evaluator = GridMap(
    evaluate_model,
    inputs=[
        Template("model"),
        Template("test_data")
    ],
    outputs=[Template("accuracy")],
    name="Evaluator"
)

# SummaryLayer: Aggregates all accuracies
class SummaryLayer(Layer):
    def __init__(self):
        super().__init__(
            name="Summary",
            inputs=[Template("accuracy")],
            outputs=[Template("final_report")]
        )
    
    def call(self, **accuracies):
        return summarize_results(**accuracies)

# 3. Create the Model
model = Model([
    iris_loader, wine_loader, 
    preprocessor, 
    splitter,
    rf_trainer, lr_trainer, 
    evaluator, 
    SummaryLayer()
])

# 4. Run the model
if __name__ == "__main__":
    print("--- Running Data Science Pipeline with GridMap ---\n")
    
    # Running the model without inputs as the loaders are the entry points
    result = model()
    
    print("\nFinal Accuracy Results:")
    for k in sorted(result.keys()):
        if "accuracy" in k:
            print(f"  {k}: {result[k]:.4f}")
    
    print(f"\nFinal report status: {result.get('final_report')}")

    G = model.create_graph({})
    A = nx.nx_agraph.to_agraph(G)
    A.draw('05_data_science_pipeline.png', prog="dot")
