from actionhypergraph.src.core.hypergraph import Relationship

class AccessRelMethods:
    pass

append_rel = Relationship('append#rel', AccessRelMethods.appendMethod)
"""Adds to the first value all the other passed values."""

contains_rel = Relationship('contains#rel', lambda x, *args : x in args)
"""Returns True if the second value passed is contained in the first."""

assign_rel = Relationship('assign#rel', lambda x, *args : x)