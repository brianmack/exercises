""" 'Friend Circles" -- compute number of connected components in
a graph."""


def _matrix_to_graph(fm):
    """ Extract nodes and edges from the friend matrix."""
    
    # for the first row, list all nodes and start collecting edges
    nodes = dict((x, set()) for x in range(len(fm[0])))

    for i, row in enumerate(fm):
        for j in range(len(row)):
            if row[j] == "Y":
                nodes[i].add(j)
    return nodes



def _search_g(g, current_node, seen_nodes=None):
    """ Recursive function to walk edges in graph.
    Inputs:
        g: (dict) graph structure with nodes (int) as keys, and
            some iterable data structure to hold which nodes each
            is connected to.
        current_node: (int) starting point on the graph for this walk
        seen_nodes: (iterable) nodes seen in any walk so far
    Returns:
        None: but seen_nodes is updated.
    """

    if seen_nodes is None:
        seen_nodes = set()

    nodes = g[current_node]

    for node in nodes:
        if node in seen_nodes:
            continue
        is_terminal = 0
        seen_nodes.add(node)
        _search_g(g, node, seen_nodes)

    return



def friend_circles(friends):
    """
    Computes number of friend circles in a graph structure where any
    connected group of friends is a 'circle', and any friend by himself
    is a 'circle'.
    Inputs:
        friends: (list of lists) matrix with one row / col for each node
            in graph, with 'Y' and 'N' indicators for the presence of an
            edge.
    Returns:
        ct: (int) count of number of circles in graph.
    """
    
    # create an efficient data structure to hold graph
    g = _matrix_to_graph(friends)

    # walk over all nodes in graph, counting circles
    ct = 0
    nodes = g.keys()
    seen_nodes = set([])
    for node in nodes:
        
        # only need to see each node once in entire process
        # because we access all accessible nodes in each walk
        if node in seen_nodes:
            continue

        # mark all nodes that we see during this walk --
        # 'seen_nodes' will be updated within function
        _search_g(g, node, seen_nodes)

        # we've marked all nodes in this circle, now increment
        # number of circles seen so far.
        ct += 1

    return ct
