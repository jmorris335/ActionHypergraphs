from src.main.hypergraph2 import *
from src.main.traversing import Pathfinder, Simulator

def main():
    plus = Relationship("plus#rel", lambda l : sum(l))
    hg = Hypergraph()
    hg.addEdge(['A', 'B'], 'E', rel=plus)
    hg.addEdge(['C', 'D'], 'F', 20, rel=plus)
    hg.addEdge(['B', 'C'], 'E', rel=plus)
    hg.addEdge(['B', 'D'], 'F', rel=plus)
    hg.addEdge(['E', 'F'], 'T', rel=plus)

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