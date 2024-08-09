# ActionHypergraphs
This repository enables usage of hypergraphs to define sand execute system models. **It is not a rigorous data storage solution. Do not use this as a database.** Note that this repo is under active development (no official release yet), therefore changes may occur rapidly. Fork the repository to create a more stable base if you want to try it. 

## Getting started
Let's build a basic action hypergraph of the following equations:
- $A + B = C$
- $A = -D$
- $E = -B$
- $D + E = F$  
- $F = -C$

First, import the classes. 
```[python]
from src.main.hypergraph import *
from src.relationships.math_rel import *
```

Second, form the nodes using a builder function. Every node needs a string label:
```[python]
A, B, C, D, E, F = HyperNode.initMany(['A', 'B', 'C', 'D', 'E', 'F])
```

To make the hypergraph we'll need to compose the 5 edges (equations) given above:
```[python]
hg = HyperGraph()
hg += HyperEdge([A, B], C, plus_rel)
hg += HyperEdge(A, D, inverse_rel)
hg += HyperEdge(E, B, inverse_rel)
hg += HyperEdge([D, E], F, plus_rel)
hg += HyperEdge(F, C, inverse_rel)
```

Now we can simulate it! Choose inputs, such as $A$ and $B$, and find a route to simulate $C$. 
```[python]
initial_conditions = dict(
    A = 3,
    B = 7,
    E = -7,
)
hg.sim([A, B], C, initial_conditions, toPrint=True)
hg.sim([A, E], C, initial_conditions, toPrint=True)
```

The output of the above should be:
```
Simulation:
  plus: [A(3), B(7)] -> [C(10)]
Simulation:
  inverse: [A(3)] -> [D(-3)]
  plus: [D(-3), E(-7)] -> [F(-10)]
  inverse: [F(-10)] -> [C(10)]
```

Check out the  [demos](https://github.com/jmorris335/ActionHypergraphs/tree/main/src/demos) directory for more examples.

## Introduction
Hypergraphs are normal graphs but without the constraint that edges must only link between two nodes. Because of this expanded generality, hypergraphs can be used to model more complex relationships. For instance, the relationship `A + B = C` is a multinodal relationship between three nodes, A, B, and C. You can think of all three nodes being linked by a 2D hyperedge, so that to move along that hyperedge you need at least two of three nodes. 

An action hypergraph is a hypergraph where the relationships are executable actions that can be carried out by some execution engine, generally via API calls. The goal is for the hypergraph to be platform agnostic, while API calls allow for edges to be processed on any available software. (The demos use Python and numpy because it's easy and free). 

Processing a series of nodes and edges (a "route") is what constitutes a simulation, so one of the uses of an actionable hypergraph is enabling high-level simulation ability from any possible entry point in a system model.

## Licensing and Usage
Author: John Morris  
Organization: PLM Center at Clemson University  
Contact: Reach out to my GitHub profile (jmorris335)  
Usage: An official release will likely have a more general license on it, but for now all rights are reserved. For usage, please reach out to the author directly.

## Vision
The goal of the graphs is to be able to store them on a software agnostic data file such as YAML or XML. For now everything is in a custom Python class, but eventually this will be transformed to a series of interfaces in Python, C++, MATLAB, and more to read in the generic hypergraph data. The interface classes would need to provide access, manipulation, and routing functionality for the generic hypergraph. 

In addition to small demonstrations in a text-based storage format, there is also the goal of moving to a more robust storage container such as [HypergraphDB](https://hypergraphdb.org/?project=hypergraphdb&page=Home). This will allow larger, distributed projects to work with greater ease than the flat file format.

Interested in contributing? Let us know, we'd love to work with you!
