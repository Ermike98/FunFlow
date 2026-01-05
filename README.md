# FunFlow

**FunFlow** is a powerful Python library designed to simplify the creation and management of complex, modular pipelines. By combining a dataflow-inspired approach with a flexible templating and tagging system, FunFlow enables developers to build scalable, production-ready workflows with minimal boilerplate.

---

## ✨ Key Features

- 🧩 **Modular Architecture**: Build workflows using reusable `Model` and `Layer` components.
- 🏷️ **Advanced Templating**: Decouple data routing from logic using a powerful tag-based terminal system.
- 🔀 **Dynamic Routing**: Automatically route data based on templates and state tags.
- ⚡ **Functional API**: Create layers instantly from standard Python functions or lambdas.
- 🗺️ **Grid Mapping**: Effortlessly run computations over combinations of inputs (perfect for hyperparameter tuning or batch processing).
- 📊 **Visual Insights**: Built-in support to visualize your computation graphs.

---

## 🚀 Quick Start

### Installation

```bash
pip install funflow
```

*For visualization support:*
```bash
pip install funflow[vis]
```

### Basic Example

Build a simple pipeline in seconds:

```python
from funflow import Model, Functional

# 1. Define your logic
def process_data(x):
    return x * 2

# 2. Build the model
model = Model(layers=[
    Functional(process_data, inputs='x', outputs='y')
])

# 3. Run it
result = model(x=10)
print(result['y']) # Output: 20
```

---

## 🧠 Advanced Capabilities

### Tag-Based Routing & GridMap

FunFlow shines in complex scenarios. Use `GridMap` to automatically handle multiple data streams using tags:

```python
from funflow import GridMap, Model, Template, NoTagFilter

# Processes any input 'data' that has an 'id' tag
layer = GridMap(
    lambda x: x**2,
    inputs=[Template("data", filters=[NoTagFilter("id")])],
    outputs=[Template("result", filters=[NoTagFilter("id")])]
)

model = Model([layer])

# Run with multiple tagged datasets
inputs = {
    "data, id:dataset_A": 10,
    "data, id:dataset_B": 20
}
result = model(**inputs)
# result contains 'result, id:dataset_A' (100) and 'result, id:dataset_B' (400)
```

---

## 🛠️ Exploring More

Check out our tiered examples to master FunFlow:

1.  **[01 Basic Pipeline](examples/01_basic_pipeline.py)**: Introduction to custom `Layer` classes.
2.  **[02 Functional Nodes](examples/02_functional_nodes.py)**: Leveraging the `Functional` API for rapid development.
3.  **[03 Tag Templating](examples/03_tag_templating.py)**: Deep dive into the power of `GridMap` and tags.
4.  **[04 Complex Routing](examples/04_complex_routing.py)**: Advanced filtering and selective joins.
5.  **[05 Data Science Pipeline](examples/05_data_science_pipeline.py)**: A real-world scenario with multiple datasets, preprocessors, and models.

---

## 🤝 Contributing

We welcome contributions! Whether it's reporting bugs, improving documentation, or submitting pull requests, your help is appreciated.

1. Fork the repo.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  Built with ❤️ by the FunFlow team.
</p>
