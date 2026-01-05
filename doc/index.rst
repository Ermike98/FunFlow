Welcome to Funflow!
==================

**Funflow** is a powerful Python library that simplifies complex pipeline creation and management.

🚀 Why Funflow?
--------------

* **Intuitive Pipeline Design**: Build data pipelines using a clear, dataflow-inspired approach
* **Modular Architecture**: Organize your workflow with ``Model`` and ``Layer`` components
* **Production Ready**: Scale from simple tasks to enterprise-level systems
* **Developer Friendly**: Minimal boilerplate, maximum productivity

Quick Start
----------

.. code-block:: python

    from funflow import Model, Functional

    # Create a simple pipeline
    def process(data):
        return data * 2

    model = Model(layers=[
        Functional(process, inputs='x', outputs='y')
    ])
    
    # Run your pipeline
    result = model(x=10)
    print(result['y']) # Output: 20

Installation
-----------

.. code-block:: bash

    pip install funflow

Core Features
-------------

* **Modular Design**: Build complex workflows from simple, reusable layers.
* **Flexible Templating**: Decouple layer implementation from data routing using a powerful tag-based system.
* **Dynamic Routing**: Automatically route data through the pipeline based on templates and state tags.
* **Functional API**: Quickly create layers from standard Python functions or lambdas.
* **Grid Mapping**: Effortlessly run computations over combinations of inputs for batch processing or hyperparameter tuning.
* **Visual Tools**: Built-in capabilities to visualize your computation graph.

.. grid:: 2

    .. grid-item-card:: 🎓 Tutorial
        :link: tutorial
        :link-type: doc

        New to Funflow? Start here with our step-by-step tutorial.

    .. grid-item-card:: 📚 User Guide
        :link: advanced
        :link-type: doc

        Detailed documentation for experienced users.

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Documentation

   getting_started
   tutorial
   advanced
   modules

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Development

   contributing
   changelog
   roadmap

Get Involved
-----------

- `GitHub Repository <https://github.com/Ermike98/FunFlow>`_
- `Report Issues <https://github.com/Ermike98/FunFlow/issues>`_

.. note::
   Funflow is actively maintained and welcomes contributions from the community!