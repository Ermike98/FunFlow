Layer
=====

The ``Layer`` is the fundamental building block of FunFlow. It represents a single step or transformation in a pipeline.

Overview
--------

A layer is an abstract class that you can subclass to implement custom logic. Each layer defines its ``inputs`` and ``outputs``, and how it transforms them in the ``call`` method.

Initialization Parameters
-------------------------

* **name**: (optional) A string name for the layer.
* **inputs**: A string, a ``Template``, or a list of these, defining what state variables the layer needs.
* **outputs**: A string, a ``Template``, or a list of these, defining what state variables the layer produces.
* **input_type**: (default: "kwargs") How the inputs are passed to the ``call`` method. Can be "args" or "kwargs".
* **output_type**: (default: "auto") How the return value of ``call`` is handled. Can be "dict", "tuple", or "auto".
* **call_type**: (default: "auto") Controls how the internal ``__call__`` handles arguments.

Implementing a Custom Layer
---------------------------

To create a custom layer, subclass ``Layer`` and implement the ``call`` method.

.. code-block:: python

   from funflow import Layer

   class MyMultiplier(Layer):
       def __init__(self, factor=2, **kwargs):
           super().__init__(**kwargs)
           self.factor = factor

       def call(self, value):
           return value * self.factor

   # Usage
   mult = MyMultiplier(factor=3, inputs='x', outputs='y')

Decoupling Logic and Names
--------------------------

One of the key benefits of FunFlow layers is that the logic inside ``call`` can use generic variable names, while the ``inputs`` and ``outputs`` mapping at the layer instance level determines which global state variables are used.

.. code-block:: python

   # In this layer, the function expects 'val'
   class Square(Layer):
       def call(self, val):
           return val ** 2

   # When instating, we map global 'input_data' to 'val' and 'val' to global 'result'
   sq = Square(inputs='input_data', outputs='result')