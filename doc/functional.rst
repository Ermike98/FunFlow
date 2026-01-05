Functional Layer
================

The ``Functional`` layer is a convenient way to wrap existing Python functions or lambdas as FunFlow layers.

Overview
--------

Instead of subclassing ``Layer`` for every simple transformation, you can use ``Functional`` to quickly integrate your logic into a pipeline.

Usage
-----

.. code-block:: python

   from funflow import Functional

   # Wrapping a lambda
   l1 = Functional(lambda x: x * 10, inputs='val', outputs='val_10')

   # Wrapping a standard function
   def process_data(data, mode='default'):
       # ... logic ...
       return processed_data

   l2 = Functional(process_data, inputs='raw', outputs='clean')

Parameters
----------

* **func**: The Python function or callable to wrap.
* **inputs**: Mapping for the function's arguments.
* **outputs**: Mapping for the function's return value.
* **call_type**: (default: "args") How the function is called. Can be "args" (positional) or "kwargs" (keyword).
* **\*\*kwargs**: Additional arguments passed to the ``Layer`` base class.
