# ActionHypergraphs
This repository enables usage of hypergraphs to define sand execute system models. **It is not a rigorous data storage solution. Do not use this as a database.** Note that this repo is under active development (no official release yet), therefore changes may occur rapidly. Fork the repository to create a more stable base if you want to try it.

# Introduction
Hypergraphs are normal graphs but without the constraint that edges must only link between two nodes. Because of this expanded generality, hypergraphs can be used to model more complex relationships. For instance, the relationship `A + B = C` is a multinodal relationship between three nodes, A, B, and C. You can think of all three nodes being linked by a 2D hyperedge, so that to move along that hyperedge you need at least two of three nodes. 

An action hypergraph is a hypergraph where the relationships are executable actions that can be carried out by some execution engine, generally via API calls. The goal is for the hypergraph to be platform agnostic, while API calls allow for edges to be processed on any available software. (The demos use Python and numpy because it's easy and free). 

Processing a series of nodes and edges (a "route") is what constitutes a simulation, so one of the uses of an actionable hypergraph is enabling high-level simulation ability from any possible entry point in a system model.

## Getting started
*Note that this demo is found in `src.demos.basic`*
Let's build a basic action hypergraph of the following equations:
- $A + B = C$
- $A = -D$
- $B = -E$
- $D + E = F$  
- $F = -C$

First, import the classes. 
```[python]
from src.main.hypergraph import Hypergraph, Relationship
```

A hypergraph consists of edges that map between a set of nodes to a single node. We provide the mapping by creating a `Relationship` object (many of which are already defined in the `relationships` module). The two relationships defined in the governing equations are addition and negation. Each relationship is a wrapper around a method that takes in a list of values and returns a single value.
```[python]
negation_rel = Relationship('negate#rel', lambda source : -source[0])
plus_rel = Relationship('plus#rel', lambda source : sum(source))
```

To make the hypergraph we'll need to compose the 5 edges (equations) given above and map them using the relationships we just made.
```[python]
hg = Hypergraph()
hg.addEdge(['A', 'B'], C, plus_rel)
hg.addEdge('A', 'D', inverse_rel)
hg.addEdge('B', 'E', inverse_rel)
hg.addEdge(['D', 'E'], 'F', plus_rel)
hg.addEdge('F', 'C', inverse_rel)
```

Compute the closure of the hypergraph by picking a set of source nodes (inputs), such as $A$ and $B$ or $A$ and $E$. Notice how providing different inputs makes different parts of the hypergraph reachable.
```[python]
print("\n**Inputs A and B**")
hg.solve(['A', 'B'], toPrint=True)
print("\n**Inputs A and E**")
hg.solve(['A', 'E'], toPrint=True)
```

Now we can simulate it! Set values for the inputs and the simulator will automatically calulate an optimized route to simulate $C$. 
```[python]
print("\n**Inputs A and B**")
hg.simulate(input_values=dict(A=3, B=7), target='C', toPrint=True)
print("\n**Inputs A and E**")
hg.simulate(input_values=dict(A=3, E=-7), target='C', toPrint=True)
```

The last output of the above should be:
```
**Inputs A and E**
   C                    
   ↓                    
   AB                   
   ↓      ↘             
   A       B            
   ↓       ↓            
 source    E            
           ↓            
         source         
**Simulation**
Inputs: A:3, E:-7
Steps:
  negate: [E:-7] -> B:7
  plus: [A:3,B:7] -> C:10
```

Check out the  [demos](https://github.com/jmorris335/ActionHypergraphs/tree/main/src/demos) directory for more examples.

## Licensing and Usage
Author: John Morris  
Organization: PLM Center at Clemson University  
Contact: Reach out to my GitHub profile (jmorris335)  
Usage: An official release will likely have a more general license on it, but for now all rights are reserved. For usage, please reach out to the author directly.

## Vision
The goal of the graphs is to be able to store them on a software agnostic data file such as YAML or XML. For now everything is in a custom Python class, but eventually this will be transformed to a series of interfaces in Python, C++, MATLAB, and more to read in the generic hypergraph data. The interface classes would need to provide access, manipulation, and routing functionality for the generic hypergraph. 

In addition to small demonstrations in a text-based storage format, there is also the goal of moving to a more robust storage container such as [HypergraphDB](https://hypergraphdb.org/?project=hypergraphdb&page=Home). This will allow larger, distributed projects to work with greater ease than the flat file format.

Interested in contributing? Let us know, we'd love to work with you!
