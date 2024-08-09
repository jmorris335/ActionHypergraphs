class Thing:
    """An object, or set of objects, forming a node in a hypergraph.
    """
    def __init__(self, label: str=None):
        """
        Creates a new `Thing` representing a real class of entities.

        Parameters
        ----------
        label : str, Optional
            The identity for the `Thing`. Uniqueness is enforced by the hypergraph.
        """
        self.label = label

    def __eq__(self, o):
        if not hasattr(o, 'label'):
            return False
        return self.label == o.label

    def __str__(self):
        return self.label

class Relationship:
    """
    A relationship that can map betweein two sets of `Object` objects.
    """
    def __init__(self, label: str, mapping: None):
        """
        Constructs a new relationship.

        Parameters
        ----------
        label : str
            The text label for the relationship. Uniqueness is enforced by the hypergraph.
        mapping : function, Optional
            The value to return from the input set of `Object` objects.
        """
        self.label = label
        if mapping is None:
            self.mapping = lambda f: f[0].value
        self.mapping = mapping

    def __call__(self, from_objects, to_objects):
        val = self.mapping(from_objects)
        for t in to_objects:
            t.value = val
        return to_objects
    
    def __str__(self):
        return self.label