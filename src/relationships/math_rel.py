import numpy as np

from actionhypergraph.src.core.hypergraph import Relationship

class RelMethods:
    def product(values):
        out = 1.0
        for x in values:
            out *= x
        return out
    
    def division(values):
        out = values[0]
        for x in values[1:]:
            out /= x
        return out
    
## Basic Operations
equal_rel = Relationship('equal#rel', lambda values : values[0])
"""Returns the value of the first input."""

increment_rel = Relationship('increment#rel', lambda values : values[0] + 1)
"""Returns the first value incremented by one."""

negate_rel = Relationship('negate#rel', lambda values: -values[0])
"""Returns the negative of the first input."""

invert_rel = Relationship('inverte#rel', lambda values: 1/values[0])
"""Returns the multiplicative inverse of the first input."""

## Rounding
floor_rel = Relationship('floor#rel', lambda values: np.floor(values[0]))
"""Returns the floor (truncated value) of the first input."""

round_rel = Relationship('round#rel', lambda values : np.round(values[0], 0))
"""Returns the nearest whole number (as a float)."""

## Algebra
plus_rel = Relationship('plus#rel', lambda values: sum(values))
"""Returns the sum of all inputs."""

mult_rel = Relationship('product#rel', RelMethods.product)
"""Returns the chain multiplication of all inputs."""

## Trigonometry
sin_rel = Relationship('sin#rel', lambda values: np.sin(values[0]))
"""Returns the sine of the first input."""

cos_rel = Relationship('cos#rel', lambda values : np.cos(values[0]))
"""Returns the cosine of the first input."""

tan_rel = Relationship('tan#rel', lambda values : np.tan(values[0]))
"""Returns the tangent of the first input."""