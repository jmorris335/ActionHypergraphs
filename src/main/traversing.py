from src.main.hypergraph2 import *
import numpy as np

class Pathfinder:
    def __init__(self, hg: Hypergraph, source: list):
        self.hg = hg
        self.source = source if isinstance(source, Node) else self.makeSourceSet(source)

        self.initializeData()
        self.p_queue = [(0.0, Edge(self.source, self.source, 0.0))]
        self.reach(self.source, 0)
        self.findPaths()

    def makeSourceSet(self, source_set: list)-> Node:
        """Makes a new simple node that points to each node in the `source_set`,
        and then makes this new node the source."""
        source_node = Node("source")
        source_node.addEdges(source_set, [0]*len(source_set))
        self.hg.simple_nodes.append(source_node)
        return source_node

    def reach(self, node: Node, set_value: int=None, increment: bool=False):
        if set_value is None:
            return self.REACH[node.label]
        elif increment:
            self.REACH[node.label] += set_value
        else:
            self.REACH[node.label] = set_value
    
    def dist(self, node: Node, set_value: float=None):
        if set_value is None: 
            return self.DIST[node.label]
        self.DIST[node.label] = set_value
    
    def last(self, node: Node, set_node: Node=None):
        if set_node == "None":
            self.LAST[node.label] = None
        elif set_node is None:
            return self.LAST[node.label]
        self.LAST[node.label] = set_node
    
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
        self.REACH = dict()
        self.DIST = dict()
        self.LAST = dict()
        for node in self.hg.simple_nodes:
            self.reach(node, 1)
            self.dist(node, np.inf)
            self.last(node, "None")
        for node in self.hg.compnd_nodes:
            self.reach(node, len(node.dependencies))
            self.dist(node, np.inf)

    def getMinQueueEl(self):
        min_val = np.inf
        min_edge = None
        for D, edge in self.p_queue:
            if D < min_val:
                min_val, min_edge = D, edge
        self.p_queue.remove((min_val, min_edge))
        return min_val, min_edge

    def findPaths(self):
        while len(self.p_queue) != 0:
            D, curr_edge = self.getMinQueueEl()
            s, t = curr_edge.source, curr_edge.target
            self.dist(t, D)
            self.last(t, s)
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
        w, t, x = edge.weight, edge.source, edge.target
        D = edge.weight + self.dist(t)
        if self.reach(x) == 1: #Unvisited
            self.reach(x, -1, increment=True)
            self.p_queue.append((D, edge))
        else:
            self.checkQueueToUpdate(D, edge)

    def getPath(self, node: Node):
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
    
    def printPath(self, target: Node)-> str:
        """
        Prints the minimum hyperpath taken from the hypergraph closure from the 
        source to the `target` node.
        """
        path = self.getPath(target)
        if path is None:
            return f"No viable path to {target}"
        col_width = min(max(len(n.label) for n in path) + 2, 8)
        cmpnd = [n for n in path if not n.isSimple()]
        num_rows = self.maxBranchLength(target) * 2 - 1
        num_cols = sum([len(n.dependencies) for n in cmpnd]) + 1
        blank = f'{' ':<{col_width}}'
        out_array = [[blank for i in range(num_cols)] for j in range(num_rows)]
        self.printPathHelper(target, out_array, col_width, 0, 0)
        out = '\n'.join([''.join([col for col in row]) for row in out_array])
        return out

    def printPathHelper(self, node: Node, out: list, width: int, row: int, col: int):
        self.printNode(node, out, row, col, width)
        if node == self.source:
            return
        row += 1
        if  node.isSimple():
            self.printLeader(out, row, col, width)
            self.printPathHelper(self.last(node), out, width, row + 1, col)
        else:
            for i, parent in enumerate(node.dependencies):
                self.printLeader(out, row, col, width, isSlant=(i != 0))
                self.printPathHelper(parent, out, width, row + 1, col)
                path = self.getPath(parent)
                cmpnd = [n for n in path if not n.isSimple()]
                num_cols = max(1, sum([len(n.dependencies) for n in cmpnd]))
                col += num_cols
        
    def printNode(self, node: Node, out: list, row: int, col: int, width: int):
        label = list(node.label[:width-2])
        if len(node.label) > width - 2:
            label[-1] = '-'
        label = ''.join(label)
        out[row][col] = f'{label: ^{width}}'

    def printLeader(self, out: list, row: int, col: int, width: int, isSlant: bool=False):
        leader = '↘' if isSlant else "↓"
        if isSlant:
            num_leading_spaces = (width - 1) // 2 - 1
            leading_spaces = ''.join([' ' for i in range(num_leading_spaces)])
            string = f'{leading_spaces}{leader}'
            out[row][col] = f'{string: <{width}}'
        else:
            out[row][col] = f'{leader: ^{width}}'
    
    def maxBranchLength(self, node: Node, num_rows: int=0):
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


    def __str__(self):
        out = '<Pathfinder object>\n'
        out += f'Minimum distance from {self.source}:\n  '
        ds = [f'{n}: {self.dist(n)}' for n in self.hg.simple_nodes]
        out += '\n  '.join(ds)
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