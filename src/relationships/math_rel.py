import numpy as np

from src.main.hypergraph2 import Relationship

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
increment_rel = Relationship('increment#rel', lambda values : values[0] + 1)
negate_rel = Relationship('negate#rel', lambda values: -values[0])
plus_rel = Relationship('plus#rel', lambda values: sum(values))
mult_rel = Relationship('product#rel', RelMethods.product)
division_rel = Relationship('division#rel', RelMethods.division)

## Trigonometry
sin_rel = Relationship('sine#rel', lambda values: np.sin(values[0]))
cos_rel = Relationship('cosine#rel', lambda values : np.cos(values[0]))