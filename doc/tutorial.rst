Tutorial
========

Basic Concepts
-------------

FunFlow is built around several core concepts. For detailed information on each, see the respective pages:

1. :doc:`layer`: Basic building blocks of computation
2. :doc:`model`: Containers that organize and connect layers
3. :doc:`functional`: Quickly wrap existing functions
4. :doc:`grid_map`: Tools for iteration and parallel processing
5. :doc:`advanced`: Dynamic patterns and flexible data flow with Templates

Creating a Simple Pipeline
------------------------

Here's a complete example of building a data processing pipeline:

.. code-block:: python

   import funflow as ff
   import numpy as np
   
   # Create a simple regression pipeline
   def normalize(data):
       return (data - np.mean(data)) / np.std(data)
   
   pipeline = ff.Model([
       ff.Functional(normalize, 
                    inputs=["X_train"], 
                    outputs=["X_train_normalized"]),
       ff.Functional(lambda x: model.fit(x), 
                    inputs=["X_train_normalized"], 
                    outputs=["trained_model"])
   ])

Working with Templates
--------------------

Templates are powerful tools for creating flexible data flows:

.. code-block:: python

   # Define templates for different data types
   raw_data = ff.Template("data", [ff.Tag("type", "raw")])
   normalized_data = ff.Template("data", [ff.Tag("type", "normalized")])
   
   # Use templates in your pipeline
   normalization = ff.Functional(
       normalize,
       inputs=[raw_data],
       outputs=[normalized_data]
   )

Advanced Usage
-------------

Grid Mapping
^^^^^^^^^^^

Use ``GridMap`` to run a function over all combinations of inputs in the state. For example, if you have multiple datasets:

.. code-block:: python

   from funflow import GridMap, Template, NoTagFilter

   # This layer will run for every variable named 'data' that has a 'batch' tag
   grid_layer = GridMap(
       process_func,
       inputs=[Template("data", filters=[NoTagFilter("batch")])],
       outputs=[Template("result", filters=[NoTagFilter("batch")])]
   )

Visualization
^^^^^^^^^^^^

Visualize your pipeline:

.. code-block:: python

   # Create and visualize the computation graph
   G = model.create_graph(inputs)
   A = nx.nx_agraph.to_agraph(G)
   A.draw('pipeline.png', prog="dot")

Real-World Example
----------------

Here's a complete example of a machine learning pipeline:

.. code-block:: python

   import funflow as ff
   from sklearn.linear_model import LinearRegression
   
   # Define templates
   untrained_model = ff.Template("untrained_model")
   trained_model = ff.Template("trained_model")
   predictions = ff.Template("predictions")
   
   # Create layers
   fit_layer = ff.Functional(
       lambda model, X, y: model.fit(X, y),
       inputs=[untrained_model, "X_train", "y_train"],
       outputs=[trained_model],
       call_type="args"
   )
   
   predict_layer = ff.Functional(
       lambda model, X: model.predict(X),
       inputs=[trained_model, "X_test"],
       outputs=[predictions],
       call_type="args"
   )
   
   # Combine into model
   model = ff.Model(
       [fit_layer, predict_layer],
       inputs=[untrained_model, "X_train", "y_train", "X_test"]
   )
   
   # Use the model
   results = model(
       untrained_model=LinearRegression(),
       X_train=X_train,
       y_train=y_train,
       X_test=X_test
   )
