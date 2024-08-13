"""
Program: hypergraph.py
Author: John Morris, jhmrrs@clemson.edu
Organization: The PLM Center at Clemson University
Purpose: Provide class objects for representing actionable hypergraphs.
Usage: All rights reserved.
Version History:
    - 0.0 [13 Aug 2024]: Initial version
"""

class Relationship:
    """A mapping between two sets, able to produce an output value given a set of
    inputs."""
    def __init__(self, label: str, mapping=None):
        """
        Constructs a new relationship.

        Parameters
        ----------
        label : str
            The unqiue text label for the relationship.
        mapping : function, Optional
            The value to return from the source set of `Node` objects. The mapping
            method takes a list as its input and returns a single value (often 
            set to the value of an output `Node`). The default option is to 
            return the input value, the "equivalent" relationship.
        """
        self.label = label
        if mapping is None:
            self.label = "equivalent#rel"
            self.mapping = lambda l: l[0]
        self.mapping = mapping

    def __call__(self, source_set: list):
        if not isinstance(source_set, list):
            source_set = [source_set]
        output = self.mapping(source_set)
        return output
    
    def __str__(self):
        return self.label

class Node:
    """A node in an FD graph.
    
    Parameters
    ----------
    label : str
        The unique identity for the `Node`. Uniqueness is enforced by the hypergraph.
    """
    def __init__(self, label: str, dependencies: list=None, value=None):
        self.label = label
        self.full_edges = list()
        self.dotted_edges = list()
        self.dependencies = dependencies
        self.value = value

    def addEdge(self, node, weight: float=1, rel: Relationship=None):
        """Adds an edge from the node to another node."""
        edge = Edge(self, node, weight, rel)
        if node.isSimple():
            self.full_edges.append(edge)
        else:
            self.dotted_edges.append(edge)

    def addEdges(self, nodes, weights: list=None, rels: list=None):
        """Helper function for adding multiple edges in a single call."""
        if weights is None:
            weights = [1 for n in nodes]
        if rels is None:
            rels = [None for n in nodes]
        if not isinstance(weights, list):
            weights = [weights]
        if not isinstance(nodes, list):
            nodes = [nodes]
        for node, weight, rel in zip(nodes, weights, rels):
            self.addEdge(node, weight, rel)

    def isSimple(self):
        """Returns true if the node is not a compound node."""
        return self.dependencies is None
    
    def __eq__(self, o):
        if hasattr(o, 'label'):
            return o.label == self.label
        return False
    
    def __str__(self):
        return self.label

class Edge:
    """An edge in a FD graph, which links two `Nodes`."""
    def __init__(self, source: Node, target: Node, weight: float=1.0, rel: Relationship=None):
        self.source = source
        self.target = target
        self.weight = weight
        self.rel = Relationship("equivalent#rel") if rel is None else rel

    def isFullEdge(self)-> bool:
        """Returns True if the `Edge` is a full edge (vs dotted)."""
        return self.target.isSimple()

    def printNodeLabel(self, node: Node, width=4):
        """Prints the node and value if possible."""
        label = str(node)
        if node.value is None:
            value = ''
        elif isinstance(node.value, float):
            value = f':{node.value:.3}'
        else:
            val_list = list(str(node.value))[:width]
            value = f':{''.join(val_list)}'
        out = f'{label}{value}'
        return out
        
    def __str__(self):
        edge_label = self.rel.label.split('#')[0]
        if not self.target.isSimple():
            return ''
        if self.source.isSimple():
            sources = self.printNodeLabel(self.source)
        else:
            s_set = list()
            for n in self.source.dependencies:
                s_set.append(self.printNodeLabel(n))
            sources = ','.join(s_set)
        out = f'{edge_label}: [{sources}] -> {self.target}:{self.target.value}'
        return out
        
class Hypergraph:
    """
    A collection of `Node` objects with access and modification methods.
    """
    def __init__(self, nodes: list=list()):
        """Creates a new hypergraph as a FD graph.
        
        Parameters
        ----------
        nodes : list
            A list of `Node` objects or strings, where the the strings will be 
            passed as the label to a new node.
        """
        self.equiv_rel = Relationship("equivalent#rel", lambda l:l[0])
        self.dotted_rel = Relationship("to#rel", lambda l:l[0])
        self.lastID = 0
        self.simple_nodes = list()
        self.compnd_nodes = list()
        for node in nodes:
            self.addNode(node)

    def __str__(self):
        out = "Hypergraph"
        out += '\n\t'.join([str(n) for n in self.getNodes()])
        return out
    
    def __iadd__(self, o):
        if isinstance(o, Node) or isinstance(o, str):
            self.addNode(o)
        elif isinstance(o, Edge):
            self.addEdge(o)
        else:
            raise Exception("New objects must be of type `Node` or `Edge`.")
        return self

    def getNodes(self)-> list:
        """Returns all the nodes in the hypergraph."""
        return self.simple_nodes + self.compnd_nodes
    
    def getNode(self, label: str, toMake: bool=False)-> Node:
        """Returns the node matching the given label."""
        nodes = self.getNodes()
        for n in nodes:
            if n.label == label:
                return n
        if toMake:
            self.addNode(label)
            return self.getNode(label, toMake=False)
        return None
    
    def setNodeValues(self, values: dict, nodes: list=None):
        """Sets the values of the given nodes.
         
        Parameters
        ----------
        values : dict | list | any
            The values to set the nodes to. If values is a dictionary, then each
            keyword of the dictionary should refer to a `Node` label. If values 
            is a list or a primitive, then it should be the same length of the 
            `nodes` parameter.
        nodes : list | Node | str, Optional
            A list of `Node` objects to set the values for. Only referenced if 
            `values` is not a dict. Can be a list of Nodes or string types, or a 
            singular object.
        
        """
        if isinstance(values, dict):
            for key, val in values.items():
                for node in self.getNodes():
                    if node.label == key:
                        node.value = val
                        break
        elif nodes is not None:
            if not isinstance(values, list):
                values = [values]
            if not isinstance(nodes, list):
                nodes = [nodes]
            for node, value in zip(nodes, values):
                label = node if isinstance(node, str) else node.label
                hg_node = self.getNode(label)
                node.value = value
        else:
            raise Exception("Inputs to `setNodeValues` were of incompatible types.")

    def assignID(self, o):
        """Assigns an int ID to the object."""
        setattr(o, 'id', self.lastID)
        self.lastID += 1
        return o

    def addNode(self, node, dependencies: list=None):
        """Adds a node to the hypergraph.
        
        Parameters
        ----------
        node : str, Node
            The node to add to the hypergraph. If of type string, then the 
            function creates a new node with the given labels and dependencies.
        dependencies : list, Optional
            A list of parent nodes for a compound node (representing a hyperedge)
            used only if constructing a new node (indicated by passing `node` as 
            a string).
        """
        if isinstance(node, str):
            node = Node(node, dependencies)
        if any(n.label == node.label for n in self.getNodes()):
            node.label = f'N{self.lastID}'
        node = self.assignID(node)
        if node.isSimple():
            self.simple_nodes.append(node)
        else:
            self.compnd_nodes.append(node)

    def addEdge(self, source: list, target: Node, weight: float=1.0, rel: Relationship=None):
        """Adds an edge (either full, dotted, or hyper) to the hypergraph.
        
        Parameters
        ----------
        source : list | Node | str
            The source set for the edge. Can be a single node. Can also be passed
            as the string (or list of strings) referencing the label of the given
            node.
        target : Node
            The target of the given edge. May be a simple or compound node. If 
            the node is simple, and the source set has a cardinality greater than
            1, then a new compound node will be created to handle the hyperedge.
        weight : float, default=1.0
            The weight of the given edge. If the target of the edge is compound 
            (or a new hyperedge is requested) then the weight is set to be 0.
        """
        if isinstance(source, Node):
            source = [source]
        for i, node in enumerate(source):
            if isinstance(node, str):
                source[i] = self.getNode(node, toMake=True)
        if isinstance(target, str):
            target = self.getNode(target, toMake=True)
        if rel is None:
            rel = self.equiv_rel
        if len(source) > 1 and target.isSimple():
            target = self.makeNewCompoundNode(source, target, weight, rel)
        if not target.isSimple():
            rel = self.dotted_rel
            weight = 0
        for node in source:
            node.addEdge(target, weight, rel)

    def makeNewCompoundNode(self, dependencies:list, target: Node, 
                            weight: float=1.0, rel: Relationship=None):
        """Creates a new compound node in the hypergraph."""
        label = ''.join([p.label[0] for p in dependencies])
        new_cmpnd_node = Node(label, dependencies)
        new_cmpnd_node.addEdge(target, weight, rel)
        self.addNode(new_cmpnd_node)
        return new_cmpnd_node

    
    
    
