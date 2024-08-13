from src.main.hypergraph import *
from src.main.traversing import Pathfinder, Simulator
from src.relationships.math_rel import *

def main():
    hg = Hypergraph()
    hg.addEdge(['A', 'B'], 'E', rel=plus_rel)
    hg.addEdge(['C', 'D'], 'F', 20, rel=plus_rel)
    hg.addEdge(['B', 'C'], 'E', rel=plus_rel)
    hg.addEdge(['B', 'D'], 'F', rel=plus_rel)
    hg.addEdge(['E', 'F'], 'T', rel=plus_rel)

    pf = Pathfinder(hg, ['A', 'B', 'C', 'D'])
    # print(pf)
    print(pf.printPath('T'))

    ics = dict(
        A = 1,
        B = 10,
        C = -3,
        D = 3,
    )
    sim = Simulator(pf, 'T', ics)
    print(sim)

    

if __name__ == '__main__':
    main()