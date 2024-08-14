from actionhypergraph.src.core.hypergraph import Hypergraph
from actionhypergraph.src.relationships.math_rel import *

def main():
    hg = makePendulumHG()

    delT = 0.05
    
    a = list()
    w = [0.0]
    th = [1.5]
    t = [0.0]
    for i in range(500):
        ics = dict(omega=w[-1], theta=th[-1], g=9.81, c=0.5, r=1.0, delT=delT)
        a.append(hg('alpha', ics))
        w.append(hg('omega+', {'alpha': a[-1], 'omega': w[-1], 'delT': delT}))
        th.append(hg('theta+', {'omega': w[-1], 'theta': th[-1], 'delT': delT}))
        t.append(hg('t+', {'t': t[-1], 'delT': delT}))

    plotPendulum(t, th)

def plotPendulum(time, theta):
    import matplotlib.pyplot as plt
    plt.plot(time, theta)
    plt.xlabel('Time (s)')
    plt.ylabel('Theta (rad)')
    plt.show()

def makePendulumHG():
    hg = Hypergraph()
    hg.addEdge(['omega', 'c'], 'beta2', rel=mult_rel)
    hg.addEdge(['beta2'], 'beta5', rel=negate_rel)
    hg.addEdge(['g', 'r'], 'beta1', rel=division_rel)
    hg.addEdge(['theta'], 'stheta', rel=sin_rel)
    hg.addEdge('beta1', 'beta4', rel=negate_rel)
    hg.addEdge(['beta4', 'stheta'], 'beta3', rel=mult_rel)
    hg.addEdge('beta3', 'alpha', rel=equal_rel, weight=100)
    hg.addEdge(['beta3', 'beta5'], 'alpha', rel=plus_rel)

    hg.addEdge(['alpha', 'delT'], 'beta_w', mult_rel)
    hg.addEdge(['omega', 'delT'], 'beta_t', mult_rel)
    hg.addEdge(['beta_w', 'omega'], 'omega+', plus_rel)
    hg.addEdge(['beta_t', 'theta'], 'theta+', plus_rel)
    hg.addEdge(['t', 'delT'], 't+', plus_rel)

    return hg

if __name__ == '__main__':
    main()