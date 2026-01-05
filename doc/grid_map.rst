Grid Map Layer
==============

The ``GridMap`` layer allows you to run a function over all possible combinations (Cartesian product) of multiple inputs.

Overview
--------

This is particularly useful for hyperparameter tuning, batch processing, or any scenario where you need to iterate over multiple dimensions of input data.

Example
-------

.. code-block:: python

   from funflow import GridMap

   def combine(a, b):
       return f"{a}-{b}"

   # This layer will run for every combination of 'data1' and 'data2'
   # If data1=['A', 'B'] and data2=[1, 2], it produces 4 outputs
   gm = GridMap(combine, inputs=['data1', 'data2'], outputs='result')

Use with Templating
-------------------

``GridMap`` is most powerful when used with the FunFlow templating system. By using templates with filters, you can dynamically generate output names that carry over the tags from the inputs.

.. code-block:: python

   from funflow import GridMap, Template, NoTagFilter

   def process(data):
       # ... logic ...
       return data * 2

   # Matches any 'input' with a 'batch' tag
   # Produces 'output' with the SAME 'batch' tag
   gm = GridMap(
       process,
       inputs=[Template("input", filters=[NoTagFilter("batch")])],
       outputs=[Template("output", filters=[NoTagFilter("batch")])]
   )

   # If state has:
   # 'input, batch: 1'
   # 'input, batch: 2'
   # The layer will produce:
   # 'output, batch: 1'
   # 'output, batch: 2'
