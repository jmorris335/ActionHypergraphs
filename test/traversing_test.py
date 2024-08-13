from src.main.hypergraph2 import *
from src.main.traversing import Pathfinder

def main():
    hg = Hypergraph()
    hg.addEdge(['A', 'B'], 'E')
    hg.addEdge(['C', 'D'], 'F', 20)
    hg.addEdge(['B', 'C'], 'E')
    hg.addEdge(['B', 'D'], 'F')
    hg.addEdge(['E', 'F'], 'T')

    pf = Pathfinder(hg, ['A', 'B', 'C', 'D'])
    print(pf)
    print(pf.printPath('T'))


if __name__ == '__main__':
    main()