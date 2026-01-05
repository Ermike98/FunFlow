
Getting Started
===============

Installation
------------

Install the latest version of ``funflow`` with ``pip``:

.. code-block:: console

   $ pip install funflow

For visualization features, install additional dependencies:

.. code-block:: console

   $ pip install funflow[vis]

Quick Start
-----------

FunFlow allows you to create complex pipelines by composing simple layers. Here is a basic example of using the Functional API:

.. code-block:: python

   from funflow import Model, Functional

   # Define a simple function
   def add(a, b):
       return a + b

   # Wrap it in a layer
   # inputs map 'x' and 'y' from global state to 'a' and 'b' in the function
   add_layer = Functional(add, inputs=['x', 'y'], outputs='sum')

   # Create a model with the layer
   model = Model(layers=[add_layer])

   # Run the model by providing the input values
   results = model(x=10, y=5)

   print(results['sum']) # Output: 15

Key Features
-----------

* **Flexible Pipeline Creation**: Build complex data processing workflows using a modular approach
* **Template System**: Powerful template-based system for dynamic data flow control
* **Visualization Support**: Built-in tools for pipeline visualization (requires ``funflow[vis]``)
* **Grid Mapping**: Advanced functionality for parallel processing and data mapping
* **Python 3.8+ Support**: Modern Python support with type hints

Requirements
-----------

* Python 3.8 or higher
* Optional visualization dependencies:
    * networkx
    * graphviz

For Development
--------------

If you want to contribute or develop with FunFlow, clone the repository and install in development mode:

.. code-block:: console

   $ git clone https://github.com/Ermike98/FunFlow
   $ cd FunFlow
   $ pip install -e .
