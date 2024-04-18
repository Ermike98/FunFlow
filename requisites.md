# Layers

### Core

* Layer
* Model

### Functional

* Functional
* Map
* Pipe

### Memory

* Cache

### Base

* Sequential
* Const
* Default

### Logic

* IfElse

# Input Output Types

Input types:
* "auto": will automatically detect
* "args": call(*inputs)
* "kwargs": call(**inputs_dict)
* "tuple": call(inputs)
* "dict": call(inputs_dict)

Output types:
* "auto": will automatically detect
* "tuple": call(...) -> tuple
* "dict": call(...) -> dict

# Templating Engine

Input and output names for each layer must be provided. To ensure maximum flexibility, however, those can also be 
provided partially at runtime using the templating engine.

## The syntax

To define a template one just have to use the template substring in the name input="series_$ticker_id$", here ticker_id is 
the template name which will be replaced at runtime by the appropriate instance name, e.g. if ticker_id="GDP" then 
input="series_GDP". 

## How it works

Templates are unique within layer. This means that if we have l=Layer(inputs=["a_$templ$", "b_$templ$], outputs=["c_$templ$"]) 
calling l(a_foo=1, b_bar=2) would result in an error as the template templ should have the same value, for the same reason
calling l(a_foo=1, b_foo=2) would be equal to {"c_foo": ...}. 

## Magics

There are a number of magic templates to trigger specific behaviours:
* "$__ALL$"
* "$__ALL_PRE$"

# Routing Algorithm

The routing algorithm is implemented in the graphlib package. The TopologicalSorter class requires a dictionary 
representing a directed acyclic graph where the keys are nodes and the values are iterables of all predecessors 
of that node in the graph
1. Determine for each output variable the list of layers from which it can be produced
2. Find for each layer the list of its predecessors: a layer is predecessor of another if the output of the first 
are used as input in the latter
3. Construct the graph to feed into the topological sorter





