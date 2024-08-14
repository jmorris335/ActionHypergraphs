from actionhypergraph.src.core.hypergraph import Hypergraph, Relationship

negation_rel = Relationship('negate#rel', lambda source : -source[0])
plus_rel = Relationship('plus#rel', lambda source : sum(source))

hg = Hypergraph()
hg.addEdge(['A', 'B'], 'C', plus_rel)
hg.addEdge('A', 'D', negation_rel)
hg.addEdge('B', 'E', negation_rel)
hg.addEdge(['D', 'E'], 'F', plus_rel)
hg.addEdge('F', 'C', negation_rel)

print("\n**Inputs A and B**")
hg.solve(['A', 'B'], toPrint=True)
print("\n**Inputs A and E**")
hg.solve(['A', 'E'], toPrint=True)

print("\n**Inputs A and B**")
hg(input_values=dict(A=3, B=7), target='C', toPrint=True)
print("\n**Inputs A and E**")
hg(input_values=dict(A=3, E=-7), target='C', toPrint=True)
