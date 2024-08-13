from src.main.hypergraph2 import *
from src.main.traversing import Pathfinder

def main():
    A, B, C, D = Node('A'), Node('B'), Node('C'), Node('D')
    E, F, T = Node('E'), Node('F'), Node('T')
    AB = Node('AB', [A, B])
    AC = Node('AC', [A, C])
    BC = Node('BC', [B, C])
    AF = Node('AF', [A, F])
    DE = Node('DE', [D, E])

    A.addEdges([AB, AF, AC])
    B.addEdges([AB, BC], [20, 20])
    C.addEdges([AC, BC])
    D.addEdges([DE])
    E.addEdges([DE])
    F.addEdges([AF])
    AB.addEdges(D, 20)
    AC.addEdges([E])
    AF.addEdges([D])
    BC.addEdges(E, 50)
    DE.addEdge(T)

    hg = Hypergraph([A, B, C, D, E, F, AB, AC, AF, BC, DE, T])
    pf = Pathfinder(hg, [A, B, C, F])
    print(pf)

    print(pf.printPath(T))


if __name__ == '__main__':
    main()