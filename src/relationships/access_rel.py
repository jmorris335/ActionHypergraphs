import numpy as np

from actionhypergraph.src.core.hypergraph import Relationship

append_rel = Relationship('append#rel', lambda values : values[0].extend(values[1:]))
"""Adds to the first value all the other passed values."""

contains_rel = Relationship('contains#rel', lambda values : values[1] in values[0])
"""Returns True if the second value passed is contained in the first."""