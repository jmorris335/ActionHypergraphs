"""
Program: hypergraph.py
Author: John Morris, jhmrrs@clemson.edu
Organization: The PLM Center at Clemson University
Purpose: Provide class objects for representing actionable hypergraphs.
Usage: All rights reserved.
Version History:
    - 0.0 [13 Aug 2024]: Initial version
"""

import hashlib

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

    def __ne__(self, o):
        return not self.__eq__(o)
    
    def __hash__(self):
        """Taken from https://stackoverflow.com/a/42089311/15496939"""
        s = self.label
        return int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % 10**8
    
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
        self.pathfinders = list()

    def __str__(self):
        out = "Hypergraph"
        out += '\n\t'.join([str(n) for n in self.getNodes()])
        return out
    
    def __call__(self, target, input_values, toPrint: bool=False):
        return self.simulate(target, input_values, toPrint)
    
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

    def addEdge(self, source: list, target: Node, rel: Relationship=None, weight: float=1.0):
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
        rel : Relationship, Optional
            The mapping between the two nodes. If `None`, then the relationship 
            default to the equivalent relationship. The relationship for a dotted 
            edge is overriden (to be the `dotted` relationship).
        weight : float, default=1.0
            The weight of the given edge. If the target of the edge is compound 
            (or a new hyperedge is requested) then the weight is set to be 0.
        """
        if not isinstance(source, list):
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
    
    def solve(self, source: list, toPrint: bool=False):
        """Caller method that computes the closure of the FD chart for the given 
        source node. Returns a `Pathfinder` object."""
        pf = Pathfinder(self, source)
        if toPrint:
            print(pf)
        self.pathfinders.append(pf)
        return pf
    
    def findPathfinder(self, input_nodes: list):
        """Finds the `Pathfinder` object that has computed closure of the same
        input set. If none is found, then the method creates one and adds it to 
        the hypergraph."""
        out_pf = None
        for pf in self.pathfinders:
            if input_nodes == pf.source_set:
                out_pf = pf
                break
        if out_pf is None:
            out_pf = Pathfinder(self, input_nodes)
            self.pathfinders.append(out_pf)
        return out_pf

    def simulate(self, target: Node, input_values: dict, toPrint: bool=False):
        """Caller method that simulates the value for the target node based on 
        the provided inputs. Returns a `Simulator` object."""
        input_nodes = [self.getNode(l) for l in input_values.keys()]
        if None in input_nodes:
            raise Exception("Input node not found in Hypergraph.")
        sim_pf = self.findPathfinder(input_nodes)
        out_val = sim_pf.simulate(target, input_values, toPrint)
        if toPrint:
            print(sim_pf.printPath(target))
            print(sim_pf.printSim(input_nodes))
        return out_val
        
class Pathfinder:
    """Object for finding the FD graph closure of a `Hypergraph`, as well as 
    optimal paths through the hypergraph. Helpful for simulations.
    """

    def __init__(self, hg: Hypergraph, source: list):
        """
        Finds the FD graph closure in the `Hypergraph` for the given source node(s).

        Parameters
        ----------
        hg : Hypergraph
            The `Hypergraph` object to compute the closure over.
        source : list | Node | str
            The nodes that act as the source set for the path (and for which closure
            is computed). Can be a list of `Node` objects or list of strings, 
            where each string references the label of a `Node` in the `Hypergraph`.
            Can also be a singular `Node` or string with equivalent meaning.
        """
        self.hg = hg
        self.findPaths(source)

    def __str__(self):
        out = '<Pathfinder object>\n'
        out += f'Minimum distance from {self.source}:\n  '
        ds = [f'{n}: {self.dist(n)}' for n in self.hg.simple_nodes]
        out += '\n  '.join(ds)
        return out
    
    def configureSource(self, source: list)-> Node:
        """Takes in a variety of inputs and returns a singular source node."""
        if not isinstance(source, list):
            source = [source]
        for i, node in enumerate(source):
            if isinstance(node, str):
                source[i] = self.hg.getNode(node)
        self.source_set = source
        self.source = source[0] if len(source)==0 else self.makeSourceSet(source)

    def makeSourceSet(self, source_set: list)-> Node:
        """Makes a new simple node that points to each node in the `source_set`,
        and then makes this new node the source."""
        source_node = Node("source")
        source_node.addEdges(source_set, [0]*len(source_set))
        self.hg.simple_nodes.append(source_node)
        return source_node

    def reach(self, node: Node, set_value: int=None, increment: bool=False):
        """Helper method to retrieve or set the REACH variable, which indicates
        whether or not the algorithm has found a viable path to the node. 
        
        Reach can have 3 different values, with the following meanings:
            - 0: The node has been reached a viable path found.
            - 1: The node has not been reached yet.
            - >1: The node is a compound node, with the value indicating the 
                number of parent nodes still to be reached.
        """
        if set_value is None:
            return self.REACH[node.label]
        elif increment:
            self.REACH[node.label] += set_value
        else:
            self.REACH[node.label] = set_value
    
    def dist(self, node: Node, set_value: float=None):
        """Helper method to retrieve or set the DIST variable, which indicates
        the minimum cost of traveling from the `source` node to the `node`."""
        if set_value is None: 
            return self.DIST[node.label]
        self.DIST[node.label] = set_value
    
    def last(self, node: Node, set_edge: Edge=None, get_edge: bool=False):
        """Helper method to retrieve or set the LAST variable, which stores the
        edge in the FD chart that leads to the given node in the optimized path.
        If called, the function returns the source node in the edge (unless 
        `get_edge` is specified.)
        """
        if set_edge == "None":
            self.LAST[node.label] = None
        elif set_edge is None:
            edge = self.LAST[node.label]
            return edge if get_edge else edge.source
        self.LAST[node.label] = set_edge
    
    def findInQueue(self, node: Node)-> tuple:
        """Returns the element in the priority queue with the given target node."""
        for el in self.p_queue:
            if el[1].target == node:
                return el
        return None
    
    def checkQueueToUpdate(self, D: float, edge: Edge):
        """Finds the element in the priority queue with an edge with the given 
        `target` node and updates the element to the provided values if the given
        edge represents a higher priority route."""
        el = self.findInQueue(edge.target)
        if el is not None:
            if D < el[0]:
                self.p_queue[self.p_queue.index(el)] = (D, edge)

    def initializeData(self):
        """Initializes the storage variables REACH, DIST, and LAST for use in 
        computing the FD chart closure."""
        self.REACH = dict()
        self.DIST = dict()
        self.LAST = dict()
        for node in self.hg.simple_nodes:
            self.reach(node, 1)
            self.dist(node, float('inf'))
            self.last(node, "None")
        for node in self.hg.compnd_nodes:
            self.reach(node, len(node.dependencies))
            self.dist(node, float('inf'))

    def getMinQueueEl(self):
        """Returns the minimum element in the priority queue. If all edges from 
        a node have been scanned, then the edge in this element is guaranteed to
        lie on an optimized hyperpath."""
        min_val = float('inf')
        min_edge = None
        for D, edge in self.p_queue:
            if D < min_val:
                min_val, min_edge = D, edge
        self.p_queue.remove((min_val, min_edge))
        return min_val, min_edge

    def findPaths(self, source: list):
        """Master algorithm for computing the distance from the `source` node to
        all other nodes in the FD chart (if possible), known as the closure."""
        self.configureSource(source)
        self.initializeData()
        self.p_queue = [(0.0, Edge(self.source, self.source, 0.0))]
        self.reach(self.source, 0)

        while len(self.p_queue) != 0:
            D, curr_edge = self.getMinQueueEl()
            s, t = curr_edge.source, curr_edge.target
            self.dist(t, D)
            self.last(t, curr_edge)
            for edge in t.full_edges:
                self.scan(edge)
            for edge in t.dotted_edges:
                z = edge.target
                self.reach(z, -1, increment=True)
                if self.reach(z) == 0:
                    self.dist(z, max([self.dist(d) for d in z.dependencies]))
                    for z_edge in z.full_edges:
                        self.scan(z_edge)

    def scan(self, edge: Edge):
        """Scans the given `edge` to see if it is a optimal edge to traverse."""
        w, t, x = edge.weight, edge.source, edge.target
        D = edge.weight + self.dist(t)
        if self.reach(x) == 1: #Unvisited
            self.reach(x, -1, increment=True)
            self.p_queue.append((D, edge))
        else:
            self.checkQueueToUpdate(D, edge)

    def getPath(self, node: Node):
        """Returns a list of all nodes in the optimal path from the `source` to
        the given `node`."""
        if self.reach(node) != 0:
            return None
        path = list()
        to_process = [node]
        while len(to_process) != 0:
            curr = to_process.pop()
            if curr == 'None':
                continue
            path.append(curr)
            if curr == self.source:
                continue
            elif curr.isSimple():
                to_process.append(self.last(curr))
            else:
                to_process.extend(curr.dependencies)
        reversed = path[::-1]
        return reversed
    
    def printPath(self, target: Node, withValue: bool=False)-> str:
        """ Prints the minimum hyperpath taken from the hypergraph closure from 
        the source to the `target` node."""
        if isinstance(target, str):
            target = self.hg.getNode(target)
        path = self.getPath(target)
        if path is None:
            return f"No viable path to {target}"
        col_width = min(max(len(n.label) for n in path) + 2, 8)
        cmpnd = [n for n in path if not n.isSimple()]
        num_rows = self.maxBranchLength(target) * 2 - 1
        num_cols = sum([len(n.dependencies) for n in cmpnd]) + 1
        blank = f'{' ':<{col_width}}'
        out_array = [[blank for i in range(num_cols)] for j in range(num_rows)]
        self.printPathHelper(target, out_array, col_width, 0, 0, withValue)
        out = '\n'.join([''.join([col for col in row]) for row in out_array])
        return out

    def printPathHelper(self, node: Node, out: list, width: int, row: int, col: int,
                        withValue: bool=False):
        """Recursive helper method for the `printPath` method."""
        self.printNode(node, out, row, col, width, withValue)
        if node == self.source:
            return
        row += 1
        if node.isSimple():
            edge = self.last(node, get_edge=True)
            rel_str = self.getRelString(edge, width) if withValue else None
            self.printLeader(out, row, col, width, withValue=rel_str)
            self.printPathHelper(edge.source, out, width, row + 1, col, withValue)
        else:
            rel_str = self.getRelString(node.full_edges[0], width) if withValue else None
            for i, parent in enumerate(node.dependencies):
                self.printLeader(out, row, col, width, isSlant=(i != 0), withValue=rel_str)
                self.printPathHelper(parent, out, width, row + 1, col, withValue)
                path = self.getPath(parent)
                cmpnd = [n for n in path if not n.isSimple()]
                num_cols = max(1, sum([len(n.dependencies) for n in cmpnd]))
                col += num_cols

    def getRelString(self, edge: Edge, width: int):
        """Gets the leader string for the relationship."""
        out = str(edge.rel).split('#')[0]
        out = list(out)[:width-2]
        out = ''.join(out)
        return out
        
    def printNode(self, node: Node, out: list, row: int, col: int, width: int, 
                  withValue: bool=False):
        """Helper function for printing `Node` labels with a specified formatting
        and spacing. Called by `printPath`."""
        label = list(node.label[:width-2])
        if len(node.label) > width - 2:
            label[-1] = '-'
        if withValue:
            val = node.value
            prefix = 3
            num_chars = min(len(str(val)), width - prefix - 2)
            last_idx = num_chars + prefix
            if isinstance(val, float):
                label[prefix:last_idx] = f':{val:.{num_chars}}'
            else:
                val_str = str(val)[:num_chars]
                label[prefix:last_idx] = f':{val_str}'
        label = ''.join(label)
        out[row][col] = f'{label: ^{width}}'

    def printLeader(self, out: list, row: int, col: int, width: int, 
                    isSlant: bool=False, withValue: str=None):
        """Helper function for printing leaders (arrows) with a specified formatting
        and spacing. Called by `printPath`."""
        leader = withValue if withValue is not None else "↘" if isSlant else "↓"
        if isSlant:
            num_leading_spaces = (width - 1) // 2 - 1
            leading_spaces = ''.join([' ' for i in range(num_leading_spaces)])
            string = f'{leading_spaces}{leader}'
            out[row][col] = f'{string: <{width}}'
        else:
            out[row][col] = f'{leader: ^{width}}'
    
    def maxBranchLength(self, node: Node, num_rows: int=0):
        """Returns the maximum length (number of nodes) in a branch of the 
        hyperpath tree. A branch is number of nodes who, along their respective
        edges, trace from the target `node` back to the `source`. 
        
        Note: Branches in the hyperpath tree occur at compound nodes. The length
        of a branch includes the maximum length of all sub-branches.
        """
        num_rows += 1
        if node == self.source:
            return num_rows
        elif node.isSimple():
            next_node = self.last(node)
            return self.maxBranchLength(next_node, num_rows)
        else:
            parents = node.dependencies
            sub_lengths = [self.maxBranchLength(p, num_rows) for p in parents]
            return max(sub_lengths)
        
    def simulate(self, target: Node, input_values: dict, toPrint: bool=False):
        """Passes the input values through the series of relationships defined
        by the class path to the `target`. Returns the found value for `target`.
        """
        self.sim_str = list()
        input_nodes = [self.hg.getNode(label) for label in input_values.keys()]
        if any([bool(self.dist(node)) for node in input_nodes]):
            self.configureSource(input_nodes)
            self.findPaths(input_nodes)

        if isinstance(target, str):
            target = self.hg.getNode(target)

        self.hg.setNodeValues(input_values)
        out_val =  self.simulationHelper(target, input_nodes)
        if toPrint:
            self.printSim(input_nodes)
        return out_val
    
    def simulationHelper(self, node, inputs: list):
        """Recursive helper for `simulate` method."""
        if node in inputs:
            return node.value
        edge = self.last(node, get_edge=True)
        rel, source = edge.rel, edge.source
        if source.isSimple():
            val = rel(self.simulationHelper(source, inputs))
        else:
            values = [self.simulationHelper(parent, inputs) for parent in source.dependencies]
            val = edge.rel(values)
        node.value = val
        self.sim_str.append(str(edge))
        return val
    
    def printSim(self, input_nodes):
        """Prints the simulation results (based on the value of `self.sim_str`).
        """
        if len(self.sim_str) == 0:
            return 'No simulation found'
        input_str = ', '.join([f'{n.label}:{n.value}' for n in input_nodes])
        out = '**Simulation**\n'
        out += 'Inputs: ' + input_str + '\n'
        out += 'Steps:\n  '
        out += '\n  '.join(self.sim_str)
        return out
    