class Edge:
    """An edge in a hypergraph, which maps two `Nodes`.
    """
    def __init__(self, source, target, weight: float=1.0):
        self.source = source
        self.target = target
        self.weight = weight

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

    def addEdge(self, node, weight: float=1):
        edge = Edge(self, node, weight)
        if node.isSimple():
            self.full_edges.append(edge)
        else:
            self.dotted_edges.append(edge)

    def addEdges(self, nodes, weights: list=None):
        if weights is None:
            weights = [1 for n in nodes]
        if not isinstance(weights, list):
            weights = [weights]
        if not isinstance(nodes, list):
            nodes = [nodes]
        for node, weight in zip(nodes, weights):
            self.addEdge(node, weight)

    def isSimple(self):
        return self.dependencies is None
    
    def __eq__(self, o):
        if hasattr(o, 'label'):
            return o.label == self.label
        return False
    
    def __str__(self):
        return self.label

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

    def addEdge(self, source: list, target: Node, weight: float=1.0):
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
        if len(source) > 1 and target.isSimple():
            target = self.makeNewCompoundNode(source, target, weight)
        if not target.isSimple():
            weight = 0
        for node in source:
            node.addEdge(target, weight)

    def makeNewCompoundNode(self, dependencies:list, target: Node, weight: float=1.0):
        """Creates a new compound node in the hypergraph."""
        label = ''.join([p.label[0] for p in dependencies])
        new_cmpnd_node = Node(label, dependencies)
        new_cmpnd_node.addEdge(target, weight)
        self.addNode(new_cmpnd_node)
        return new_cmpnd_node

    
    
    
