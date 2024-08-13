class Edge:
    def __init__(self, source, target, weight: float=1.0):
        self.source = source
        self.target = target
        self.weight = weight

class Node:
    def __init__(self, label: str, dependencies: list=None):
        self.label = label
        self.full_edges = list()
        self.dotted_edges = list()
        self.dependencies = dependencies

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
    def __init__(self, nodes: list):
        self.simple_nodes = [n for n in nodes if n.isSimple()]
        self.compnd_nodes = [n for n in nodes if not n.isSimple()]

    
    
    
