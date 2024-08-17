from actionhypergraph import Hypergraph, Relationship
from actionhypergraph import math_rel

hg = Hypergraph()
hg.addEdge(['A', 'step'], 'A+', math_rel.plus_rel)
hg.addEdge('A+', 'A', math_rel.equal_rel)
hg.addEdge('A0', 'A', math_rel.equal_rel)

hg.simulate('A+', {'A0':0, 'step':1}, toPrint=True)