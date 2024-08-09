if __name__ == '__main__':
    import sys
    sys.path.append('.')

from src.main.hypergraph import HyperEdge, HyperGraph, HyperNode
from src.relationships.math_rel import *
from src.main.hypergraph import Router

def main():
    hg = HyperGraph()
    A = HyperNode('A')
    B = HyperNode('B')
    C = HyperNode('C')
    D = HyperNode('D')
    E = HyperNode('E')
    F = HyperNode('F')
    
    hg += HyperEdge([A, F, B], [E], plus_rel)
    hg += HyperEdge(A, F, increment_rel)
    hg += HyperEdge(A, D, increment_rel)
    hg += HyperEdge(D, C, increment_rel)
    hg += HyperEdge(E, C, increment_rel)

    router = Router(hg, A, C)
    route = router.routes[0]
    print(f"Inputs: [" + ", ".join([str(node) for node in route.getInputs()]) + "]")
    sim_val = route([5, 6, 10], toPrint=True)

    print(route)

    reduced_route = router.reduce(route)
    print(reduced_route)
    reduced_route([5, 10], toPrint=True)

if __name__ == '__main__':
    main()