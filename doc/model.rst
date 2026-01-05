Model
=====

A ``Model`` is a collection of layers organized into a directed acyclic graph (DAG). It manages the execution flow and the shared state between layers.

Overview
--------

The ``Model`` class is itself a subclass of ``Layer``, meaning a model can be used as a layer within another model, allowing for hierarchical pipeline design.

Initialization Parameters
-------------------------

* **layers**: A single ``Layer`` or a list of ``Layer`` instances to include in the model.
* **inputs**: (optional) A list of required input names for the entire model.
* **outputs**: (optional) A list of expected output names from the model.

Execution Flow
--------------

When a model is called, it:
1.  Analyzes the dependencies between layers based on their ``inputs`` and ``outputs``.
2.  Determines a topological order for execution.
3.  Executes layers sequentially (or potentially in parallel where dependencies allow).
4.  Updates a global state dictionary with the results of each layer.

Example
-------

.. code-block:: python

   from funflow import Model, Functional

   l1 = Functional(lambda x: x + 1, inputs='a', outputs='b')
   l2 = Functional(lambda x: x * 2, inputs='b', outputs='c')

   model = Model(layers=[l1, l2])

   # Running the model
   results = model(a=5)
   print(results['c']) # (5 + 1) * 2 = 12

Visualization
-------------

If you have ``funflow[vis]`` installed, you can visualize the execution graph:

.. code-block:: python

   G = model.create_graph(inputs={'a': 5})
   # You can then use networkx or other tools to draw G