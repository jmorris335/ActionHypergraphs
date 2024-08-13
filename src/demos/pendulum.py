from src.main.hypergraph import Hypergraph
from src.main.traversing import Pathfinder, Simulator
from src.relationships.math_rel import *

def main():
    hg = makePendulumHG()

    pf = Pathfinder(hg, ['omega', 'theta', 'g', 'r', 'c'])
    print(pf)
    print(pf.printPath('alpha'))

    ics = dict(
        omega = 1.0,
        theta = 0.0,
        c = 1.0,
        g = 9.81,
        r = 1.0,
    )
    sim = Simulator(pf, 'alpha', ics)
    print(sim)

def makePendulumHG():
    hg = Hypergraph()
    hg.addEdge(['omega', 'c'], 'beta2', rel=mult_rel)
    hg.addEdge(['beta2'], 'beta5', rel=negate_rel)
    hg.addEdge(['g', 'r'], 'beta1', rel=division_rel)
    hg.addEdge(['theta'], 'stheta', rel=sin_rel)
    hg.addEdge('beta1', 'beta4', rel=negate_rel)
    hg.addEdge(['beta4', 'stheta'], 'beta3', rel=mult_rel)
    hg.addEdge('beta3', 'alpha', 100, rel=equal_rel)
    hg.addEdge(['beta3', 'beta5'], 'alpha', rel=plus_rel)

    return hg

if __name__ == '__main__':
    main()