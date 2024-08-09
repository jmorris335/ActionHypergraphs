if __name__ == '__main__':
    import sys
    sys.path.append('.')

from src.main.hypergraph import HyperEdge, HyperGraph, HyperNode
from src.relationships.math_rel import *

def main():
    g = HyperNode('g', 9.81)
    theta, omega, alpha = HyperNode.initMany(['theta','omega', 'alpha'])
    r, c, stheta = HyperNode.initMany(['r', 'c', 'stheta'])
    beta1, beta2, beta3, beta4, beta5 = HyperNode.initMany([ 'b1', 'b2', 'b3', 'b4', 'b5'])

    hg = HyperGraph()
    hg += HyperEdge([omega, c], beta2, mult_rel)
    hg += HyperEdge(beta2, beta5, inverse_rel)
    hg += HyperEdge([g, r], beta1, division_rel)
    hg += HyperEdge(theta, stheta, sin_rel)
    hg += HyperEdge(beta1, beta4, inverse_rel)
    hg += HyperEdge([beta4, stheta], beta3, mult_rel)
    hg += HyperEdge(beta3, alpha, equal_rel)
    hg += HyperEdge([beta3, beta5], alpha, plus_rel)

    router = hg.router(theta, alpha)
    route = router.getShortestRoute()
    router.supplement(r, route)
    print(route.getInputs(toString=True))
    # route = router.getRoute([g, theta, r])
    print(route)
    route([0, 9.81, 1.0], toPrint=True)

if __name__ == '__main__':
    main()