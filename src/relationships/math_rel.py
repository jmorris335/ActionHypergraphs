import numpy as np

from src.main.objects import Relationship

class RelMethods:
    def product(nodes):
        out = 1.0
        for n in nodes:
            out *= n.value
        return out
    
    def division(nodes):
        out = nodes[0].value
        for n in nodes[1:]:
            out /= n.value
        return out
    
## Basic Operations
equal_rel = Relationship('equal', lambda nodes : [n.value for n in nodes])
increment_rel = Relationship('increment', lambda nodes : nodes[0].value + 1)
inverse_rel = Relationship('inverse', lambda nodes: -nodes[0].value)
plus_rel = Relationship('plus', lambda nodes: sum([n.value for n in nodes]))
mult_rel = Relationship('product', RelMethods.product)
division_rel = Relationship('division', RelMethods.division)

## Trigonometry
sin_rel = Relationship('sine', lambda nodes: np.sin(nodes[0].value))
cos_rel = Relationship('cosine', lambda nodes : np.cos(nodes[0]))