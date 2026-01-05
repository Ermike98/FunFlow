Advanced Features
=================

FunFlow's advanced features allow for highly dynamic and flexible pipeline architectures through a powerful templating engine and dynamic routing system.

Templating System
-----------------

The templating system decouples the internal logic of a layer from the names of the variables in the global state. This allows you to write generic layers that can be applied to many different data sources.

.. code-block:: python

   from funflow import Template, Tag, NoTagFilter

   # A template that matches the name "data" and MUST have a tag "version"
   t = Template("data", filters=[NoTagFilter("version")])
   
   # You can instantiate it with a specific tag value
   val = t.instantiate([Tag("version", "1")])
   print(str(val)) # Output: data, version: 1

Dynamic Routing
---------------

By using templates in the ``inputs`` and ``outputs`` of layers, you can create pipelines where data is routed based on tags. FunFlow automatically resolves the templates based on the available data in the model's state.

.. code-block:: python

   from funflow import Functional, Template, NoTagFilter

   # This layer takes 'input' with any 'id' and produces 'output' with the same 'id'
   # FunFlow will automatically resolve 'id' from the available state tags.
   l = Functional(lambda x: x * 2,
                  inputs=Template("input", filters=[NoTagFilter("id")]),
                  outputs=Template("output", filters=[NoTagFilter("id")]))

Tag Filters
-----------

Tag filters allow you to select specific data subsets from the state based on complex criteria.

.. code-block:: python

   from funflow import ValueTagFilter, NoTagFilter

   # Match a specific tag value
   f1 = ValueTagFilter("experiment", "A")

   # Match any tag value for a given name
   f2 = NoTagFilter("session_id")

Custom Layer Development
------------------------

Beyond the functional API, you can create fully custom layers by inheriting from the ``Layer`` class. This gives you maximum control over the initialization and execution logic.

.. code-block:: python

   from funflow import Layer

   class CustomLayer(Layer):
       def __init__(self, **kwargs):
           super().__init__(**kwargs)
           # Custom initialization...

       def call(self, **kwargs):
           # Custom processing...
           return {"result": 42}