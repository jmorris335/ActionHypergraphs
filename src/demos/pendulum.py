from src.main.hypergraph import HyperEdge, HyperGraph, HyperNode
from src.relationships.math_rel import *

def main():
    hg = makePendulumHG()
    omega, alpha, r, theta = hg.getNodes(['omega', 'alpha', 'r', 'theta'])

    router = hg.router(theta, alpha)
    route = router.getShortestRoute()
    router.supplement([r], route)
    print(route)

    ics = dict(
        omega = 1.0,
        theta = 0.0,
        c = 1.0,
        g = 9.81,
        r = 1.0,
    )
    route.simulate(ics, toPrint=True)

def makePendulumHG():
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

    return hg

if __name__ == '__main__':
    main()