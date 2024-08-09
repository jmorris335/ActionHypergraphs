from src.main.objects import Thing, Relationship 

class HyperNode(Thing):
    """A node in an hypergraph, which contains a `Object` and traversing methods.
    
    Parameters
    ----------
    label : str, Optional
            The identity for the `Thing`. Uniqueness is enforced by the hypergraph.
    id : int, Optional
        The ID for the `Object`, generally set by the `HyperGraph`.
    """
    def __init__(self, label: str, value=None, id: int=-1):
        super().__init__(label)
        self.id = id
        self.value = value
        self.from_edges = list()
        self.to_edges = list()

    def initMany(labels: list, values: list=None, ids: list=None):
        """Builder method for constructing many `HyperNode` objects at once."""
        out = list()
        if values is None:
            values = [None for l in labels]
        if ids is None:
            ids = [-1 for l in labels]
        for label, value, id in zip(labels, values, ids):
            out.append(HyperNode(label, value, id))
        return out

class HyperEdge:
    """
    An edge in a hypergraph, which maps two sets of `Object` objects by a `Relationship`.
    """
    def __init__(self, from_nodes: list, to_nodes: list, rel: Relationship, id: int=-1,):
        """
        Constructs a new `HyperEdge` for use in a `HyperGraph` object.

        Parameters
        ----------
        from_objects : list
            List of `Object` objects that form the input set for the edge.
        to_objects : list
            List of `Object` objects that are mapped to from the input set.
        rel : Relationship
            The mapping between `from_objects` and `to_objects`.
        id : int, Optional
            The identification number (generally assigned by the `HyperGraph`.)
        """
        if not isinstance(from_nodes, list):
            from_nodes = [from_nodes]
        self.from_nodes = from_nodes
        if not isinstance(to_nodes, list):
            to_nodes = [to_nodes]
        self.to_nodes = to_nodes
        self.id = id
        self.rel = rel
    
    def map(self, from_nodes: list=None):
        if from_nodes is None:
            from_nodes = self.from_nodes
        return self.rel(from_nodes, self.to_nodes)
    
    def __str__(self):
        out = str(self.rel) + ': '
        out += '(' + ', '.join([str(f) for f in self.from_nodes]) + ')'
        out += '-> (' + ', '.join([str(t) for t in self.to_nodes]) + ')'
        return out
    
    def mapsFrom(self, label):
        """Returns True if the object is in the domain of the `HyperEdge`"""
        if isinstance(label, HyperNode) or isinstance(label, Thing):
            label = label.label
        return label in [o.label for o in self.from_nodes]
    
    def mapsTo(self, label):
        """Returns True if the object is in the codomain of the `HyperEdge`"""
        if isinstance(label, HyperNode) or isinstance(label, Thing):
            label = label.label
        return label in [n.label for n in self.to_nodes]

class HyperGraph:
    """
    A collection of `HyperEdge` objects and traversing methods.
    """
    def __init__(self, startID: int=1):
        """Constructs a new `HyperGraph`."""
        self.edges = list()
        self.nodes = list()
        self.lastID = startID

    def assignID(self, o):
        """Assigns an int ID to the object."""
        setattr(o, 'id', self.lastID)
        self.lastID += 1
        return o
    
    def addNode(self, node: HyperNode):
        """Adds a `HyperNode` to the graph. Enforces uniqueness."""
        if any(n.label == node.label for n in self.nodes):
            return
        for edge in self.edges:
            self.updateLinks(node, edge)
        self.nodes.append(self.assignID(node))

    def addEdge(self, edge: HyperEdge):
        """Adds a `HyperEdge` to the graph. Enforces uniqueness."""
        self.edges.append(self.assignID(edge))
        new_nodes = edge.from_nodes + edge.to_nodes
        for new_node in new_nodes:
            self.addNode(new_node)

        for node in self.nodes:
            self.updateLinks(node, edge)

    def updateLinks(self, node: HyperNode, edge: HyperEdge):
        """Updates the node if linked to the edge."""
        if edge.mapsTo(node):
            if edge not in node.from_edges:
                node.from_edges.append(edge)
        if edge.mapsFrom(node):
            if edge not in node.to_edges:
                node.to_edges.append(edge)

    def __add__(self, graph):
        if not hasattr(graph, 'edges'):
            raise Exception("Object must be of same type as `HyperGraph`")
        for edge in graph.edges:
            self.addEdge(edge)
        return self

    def __iadd__(self, o):
        if isinstance(o, HyperNode):
            self.addNode(o)
        elif isinstance(o, HyperEdge):
            self.addEdge(o)
        else:
            raise Exception("New objects must be of type `HyperNode` or `HyperEdge`.")
        return self

    def __str__(self):
        out = "HyperGraph:"
        out += '\n\t'.join([str(e) for e in self.edges])
        return out
    
    def getNode(self, label: str)-> HyperNode:
        """Returns the node in the hypergraph with the given label."""
        for node in self.nodes:
            if node.label == label:
                return node
        return None
    
    def getNodes(self, labels: list)-> list:
        """Returns a list of nodes from the hypergraph with the given labels."""
        return [self.getNode(l) for l in labels]
    
    def getRoutes(self, start_node: HyperNode, end_node: HyperNode):
        """Returns all possible simulations between the given nodes."""
        return self.router(start_node, end_node).routes
    
    def router(self, start_node, end_node):
        """Returns a `Router` object for doing traversal operations."""
        return Router(self, start_node, end_node)
    
    def sim(self, start_node: HyperNode, end_node: HyperNode, ics=None, toPrint: bool=False):
        """Simulates the graph at a starting node through the most direct route."""
        router = Router(self, start_node, end_node)
        if len(router.routes) == 0:
            return None
        route = router.getShortestRoute()
        return route(ics, toPrint)
    
class Route:
    """A simulation route that is composed of RouteNodes."""
    class RouteStep:
        """Container class for a step in the route."""
        def __init__(self, next_node: HyperNode, edge: HyperEdge):
            self.next_node = next_node
            self.edge = edge

        def step(self, input_values: list=None, toPrint: bool=False):
            """Set the values for the `to_nodes` during a simulation. `inputs` is a list
            of values to assign to the `from_nodes` if not already assigned."""
            if input_values is not None:
                for node,input in zip(self.edge.from_nodes, input_values):
                    node.value = input
            self.edge.map()
            if toPrint:
                out = f"  {self.edge.rel}: ["
                from_nodes = [f"{n}({n.value})" for n in self.edge.from_nodes]
                out += ", ".join(from_nodes)
                out += f"] -> [{self.next_node}({self.next_node.value})]"
                print(out)

    def __init__(self, steps: list=list()):
        self.input_nodes = list()
        self.steps = steps
        if len(steps) > 0:
            self.findInputs()

    def __len__(self):
        return len(self.steps)
    
    def __iadd__(self, new_route):
        if isinstance(new_route, Route):
            self.addRoute(new_route)
            return self
        else:
            raise TypeError(f"Cannot add object of type {type(new_route)} to `Route`")
    
    def __call__(self, ics: list=None, toPrint: bool=False):
        return self.simulate(ics, toPrint)
    
    def __str__(self):
        out = 'Route:\n  '
        out += self.getInputs(toString=True) + '\n  '
        out += '\n  '.join([str(s.edge) for s in self.steps])
        return out
        
    def addStep(self, next_node: HyperNode, edge: HyperEdge):
        """Adds a step to the route """
        route_step = self.RouteStep(next_node, edge)
        self.steps.append(route_step)

    def addRoute(self, new_route):
        """Adds a new route to the route."""
        new_node = new_route.steps[-1].next_node
        for i in range(len(self.steps)):
            if new_node in self.steps[i].edge.from_nodes:
                self.steps[i:i] = new_route.steps
                return
        self.steps[0:0] = new_route.steps

    def getAllNodes(self)-> list:
        """Returns a list of all nodes that are in the given route."""
        out = list()
        for step in self.steps:
            nodes = step.edge.to_nodes + step.edge.from_nodes
            out += [n for n in nodes if n not in out]
            if step.next_node not in out:
                out.append(step.next_node)
        return out

    def findNode(self, node: HyperNode)-> list:
        """Returns a list of all steps that the link to the given node."""
        out = list()
        for step in self.steps:
            if node in step.edge.to_nodes:
                out.append(step)
            elif node == step.next_node:
                out.append(step)
        return out

    def getInputs(self, toString: bool=False)-> list:
        """Returns a list of all inputs necessary for the simulation."""
        self.findInputs()
        if toString:
            return 'Inputs: [' + ', '.join([str(n) for n in self.input_nodes]) + ']'
        return self.input_nodes
    
    def findInputs(self):
        """Searches the established route for all independent nodes."""
        self.input_nodes = list()
        to_nodes = list()
        for step in self.steps:
            for node in step.edge.to_nodes:
                if node not in to_nodes:
                    to_nodes.append(node)
        for step in self.steps:
            for node in step.edge.from_nodes:
                if node not in self.input_nodes and node not in to_nodes:
                    self.input_nodes.append(node)

    def simulate(self, initial_conditions=None, toPrint: bool=False):
        """Simulates the route, returning the value of the end node."""
        if toPrint:
            print("Simulation:")
        if initial_conditions is not None:
            self.setNodeValues(initial_conditions)
        for step in self.steps:
            step.step(toPrint=toPrint)
        return self.steps[-1].next_node.value
    
    def setNodeValues(self, values=None):
        """Sets the values of the given nodes. If values is a dict then each
        keyword must be a node label. If `values` is a list then it is paired
        with the class input nodes."""
        self.findInputs()
        if isinstance(values, dict):
            for key, val in values.items():
                for node in self.input_nodes:
                    if node.label == key:
                        node.value = val
                        break
        else:
            for node, ic in zip(self.input_nodes, values):
                node.value = ic

class Router:
    def __init__(self, hg: HyperGraph, root: HyperNode, destination: HyperNode):
        self.hg = hg
        self.start = root
        self.end = destination
        self.routes = list()
        self.findRoutes()

    def findRoutes(self):
        """Returns a list of lists of `RouteNode` objects describing possible routes 
        in the graph."""
        self.unexplored_nodes = [n for n in self.hg.nodes]
        self.unexplored_nodes.remove(self.start)

        for edge in self.start.to_edges:
            for node in edge.to_nodes:
                self.routeStep(node, edge, list())
        
        return self.routes
    
    def routeStep(self, this_node: HyperNode, this_edge: HyperEdge, path: list):
        """Recursive step for building a route."""
        path.append(Route.RouteStep(this_node, this_edge))

        if this_node == self.end:
            route = Route([step for step in path])
            self.routes.append(route)
            return
        
        self.exploreNextNode(this_node, path)
        return 
    
    def exploreNextNode(self, this_node: HyperNode, path: list):
        """Helper function for recursion. Sets up the next node to recusively explore."""
        self.unexplored_nodes.remove(this_node)
        for next_edge in this_node.to_edges:
            for next_node in next_edge.to_nodes:
                if next_node in self.unexplored_nodes:
                    self.routeStep(next_node, next_edge, path)

    def getShortestRoute(self, routes: list=None)-> Route:
        """Returns the most direct route (as counted by number of edges to traverse)."""
        if routes is None:
            routes = self.routes
        if len(routes) == 0:
            return None
        route_lengths = [len(r) for r in routes]
        min_route = routes[route_lengths.index(min(route_lengths))]
        return min_route
    
    def reduce(self, route: Route):
        """Reduces the number of necessary inputs by calculating direct routes from the
        starting node."""
        for node in route.getInputs():
            alt_router = Router(self.hg, self.start, node)
            for alt_route in alt_router.routes:
                if (len(alt_route.getInputs())) == 1:
                    route += alt_route
                    break
        return route
    
    def supplement(self, nodes: list, route: Route):
        """Adds the shortest path that adds the given nodes to the route 
        (if possible)."""
        if not isinstance(nodes, list):
            nodes = [nodes]
        for node in nodes:
            if len(route.findNode(node)) > 0:
                continue #node already in route
            possible_routes = list()
            for route_node in route.getAllNodes():
                min_route = Router(self.hg, node, route_node).getShortestRoute()
                if min_route is not None:
                    possible_routes.append(min_route)
            route += self.getShortestRoute(possible_routes)
    
    def getRoute(self, nodes: list):
        """Returns the shortest route containing all the nodes given (if any)."""
        found_routes = list()
        for route in self.routes:
            if all([len(route.findNode(n)) != 0 for n in nodes]):
                found_routes.append(route)
        return self.getShortestRoute(found_routes)
            