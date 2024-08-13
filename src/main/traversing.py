"""
Program: traversing.py
Author: John Morris, jhmrrs@clemson.edu
Organization: The PLM Center at Clemson University
Purpose: Provide class objects for traversing actionable hypergraphs.
Usage: All rights reserved.
Credits: Primary algorithms derived by G. Ausiello, R. Giaccio, G. Italiano, 
    and U. Nanni, “Optimal Traversal of Directed Hypergraphs,” International 
    Computer Science Institute, Berkeley, CA, ICSI Technical Report ICSI 
    TR-92-073, Sep. 1992. Accessed: Aug. 09, 2024. [Online]. Available: 
    https://www.icsi.berkeley.edu/icsi/publication_details?n=778
Version History:
    - 0.0 [13 Aug 2024]: Initial version
"""

from src.main.hypergraph2 import Node, Edge, Hypergraph

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
        if not isinstance(source, list):
            source = [source]
        for i, node in enumerate(source):
            if isinstance(node, str):
                source[i] = hg.getNode(node)
        self.source = source[0] if len(source)==0 else self.makeSourceSet(source)

        self.initializeData()
        self.p_queue = [(0.0, Edge(self.source, self.source, 0.0))]
        self.reach(self.source, 0)
        self.findPaths()

    def __str__(self):
        out = '<Pathfinder object>\n'
        out += f'Minimum distance from {self.source}:\n  '
        ds = [f'{n}: {self.dist(n)}' for n in self.hg.simple_nodes]
        out += '\n  '.join(ds)
        return out

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

    def findPaths(self):
        """Master algorithm for computing the distance from the `source` node to
        all other nodes in the FD chart (if possible), known as the closure."""
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

class Simulator:
    def __init__(self, pf: Pathfinder, target: Node, input_values: dict):
        self.pf = pf
        self.out_str = list()
        self.simulate(target, input_values)

    def simulate(self, target: Node, input_values: dict, input_nodes: list=None):
        if isinstance(target, str):
            target = self.pf.hg.getNode(target)
        self.target = target
        self.pf.hg.setNodeValues(input_values, input_nodes)
        if input_nodes is None:
            input_nodes = [self.pf.hg.getNode(label) for label in input_values.keys()]
        self.input_nodes = input_nodes
        if isinstance(target, str):
            target = self.pf.hg.getNode(target)
        return self.simulationHelper(target, input_nodes)
    
    def simulationHelper(self, node, inputs: list):
        if node in inputs:
            return node.value
        edge = self.pf.last(node, get_edge=True)
        rel, source = edge.rel, edge.source
        if source.isSimple():
            val = rel(self.simulationHelper(source, inputs))
        else:
            values = [self.simulationHelper(parent, inputs) for parent in source.dependencies]
            val = edge.rel(values)
        node.value = val
        self.out_str.append(str(edge))
        return val
    
    def printSimTree(self)-> str:
        return self.pf.printPath(self.target, withValue=True)
    
    def __str__(self):
        nodes = self.pf.getPath(self.target)
        input_str = ', '.join([f'{n.label}:{n.value}' for n in self.input_nodes])
        out = '**Simulation**\n'
        out += 'Inputs: ' + input_str + '\n'
        out += 'Steps:\n  '
        out += '\n  '.join(self.out_str)
        return out
        
    
            
if __name__ == '__main__':
    A, B, C, D = Node('A'), Node('B'), Node('C'), Node('D')
    E, F, G, H = Node('E'), Node('F'), Node('G'), Node('H')
    BF = Node('BF', [B, F])
    BFG = Node('BFG', [B, F, G])
    CD = Node('CD', [C, D])

    A.addEdge(B)
    B.addEdges([BF, BFG])
    C.addEdges([A, F, D, CD])
    D.addEdge(CD)
    F.addEdges([B, BF, BFG])
    G.addEdge(BFG)
    H.addEdge(E)
    BF.addEdge(E)
    BFG.addEdge(H)
    CD.addEdge(G)

    hg = Hypergraph([A, B, C, D, E, F, G, H, BF, BFG, CD])
    pf = Pathfinder(hg, C)
    # print(pf)

    print(pf.printPath(H))