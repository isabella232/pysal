"""
Winged-edge Data Structure for Networks

"""

__author__ = "Sergio J. Rey <srey@asu.edu>"



def get_regions(graph):
    """
    Find the connected regions formed by the links partitioning of the plane

    Parameters
    ----------

    graph: a networkx graph assumed to be planar



    Returns
    -------

    regions: a list of regions, with each reach a tuple of the nodes tracing
    out the region in closed-cartographic form. First region is the external
    polygon for the plane.


    """
    regions = nx.cycle_basis(G)
    for region in regions:
        region.append(region[0])
    regions.insert(0,())
    return regions

def pcw(coords):
    """ test if polygon coordinates are clockwise ordered """
    n = len(coords)
    xl = coords[0:n-1,0]
    yl = coords[1:,1]
    xr = coords[1:,0]
    yr = coords[0:n-1,1]
    a = xl*yl - xr*yr
    area = a.sum()
    if area < 0:
        return 1
    else:
        return 0
     
class WingEdge(object):
    """Data Structure for Networks
    
    Parameters
    ----------

    G: networkx graph

    P: nx2 array of coordinates for nodes in G


    Notes
    -----

    This implementation follows the description in Okabe and Sugihara (2012)
    "Spatial Analysis Along Networks: Statistical and Computational Methods."
    Wiley. Details are from Section 3.1.2.

    As the start_c, end_c, start_cc, and end_cc pointers are only vaguely
    described, the logic from
    http://www.cs.mtu.edu/~shene/COURSES/cs3621/NOTES/model/winged-e.html is
    used to implement these points
    
    """
    def __init__(self, G, P):
        super(WingEdge, self).__init__()
        self.G = G 
        self.P = P
        self.regions = get_regions(G)

        self.node_link = {}     # key: node, value: incident link (edge)
        self.region_link = {}   # key: region (face), value: incident link (edge) 
        self.start_node = {}    # key: link (edge), value: start node 
        self.end_node = {}      # key: link (edge), value: end node 
        self.right_region = {}  # key: link (edge), value: region (face)
        self.left_region = {}   # key: link (edge), value: region (face)
        self.start_c_link = {}  # key: link, value: first incident cw link 
        self.start_cc_link = {} # key: link, value: first incident ccw link 
        self.end_c_link = {}    # key: link, value: first incident c link (end node)
        self.end_cc_link = {}   # key: link, value: first incident ccw link (end node)

        edges = G.edges()
        for edge in edges:
            o,d = edge
            if not o in self.node_link:
                self.node_link[o] = edge

            if not edge in self.start_node:
                self.start_node[edge] = o

            if not edge in self.end_node:
                self.end_node[edge] = d


        for r, region in enumerate(self.regions):
            if not r in self.region_link and r > 0:
                self.region_link[r] = (region[0], region[1])
            if r > 0:
                rcw = pcw(self.P[region[:-1],:])
                for i in xrange(len(region)-1):
                    o,d = region[i:i+2]
                    if rcw:
                        self.right_region[(o,d)] = r
                        self.left_region[(d,o)] = r
                    else:
                        self.left_region[(o,d)] = r
                        self.right_region[(d,o)] = r

        # now for external face
        G = self.G.to_directed()

        missing = [ edge for edge in G.edges() if edge not in self.left_region]
        for edge in missing:
            self.left_region[edge] = 0

        missing = [ edge for edge in G.edges() if edge not in self.right_region]
        for edge in missing:
            self.right_region[edge] = 0
        
        # ccw and cw links
        for edge in self.left_region:
            left_r = self.left_region[edge]
            right_r = self.right_region[edge]
            self.start_c_link[edge] = None
            self.start_cc_link[edge] = None
            self.end_c_link[edge] = None
            self.end_cc_link[edge] = None
            if left_r > 0:
                region = self.regions[left_r]
                n = len(region)
                o = region.index(edge[0])
                d = region.index(edge[1])
                # predecessor
                pred = None
                nxt = None
                if o == 0:
                    pred = (region[-2], region[-1])
                    nxt = (region[o+1], region[o+2])

                if o == n-2:
                    nxt = (region[0], region[1])
                    pred = (region[o-1], region[o])

                if o > 0 and o < n-2:
                    nxt = (region[o+1], region[o+2])
                    pred = (region[o-1], region[o])

                self.start_c_link[edge] = pred
                self.start_cc_link[edge] = nxt

            if right_r > 0:
                region = self.regions[right_r]
                n = len(region)
                o = region.index(edge[0])
                d = region.index(edge[1])
                # predecessor
                pred = None
                nxt = None
                if o == 0:
                    pred = (region[-2], region[-1])
                    nxt = (region[o+1], region[o+2])

                if o == n-2:
                    nxt = (region[0], region[1])
                    pred = (region[o-1], region[o])

                if o > 0 and o < n-2:
                    nxt = (region[o+1], region[o+2])
                    pred = (region[o-1], region[o])

                self.end_c_link[edge] = pred
                self.end_cc_link[edge] = nxt

        
class Vertex(object):
    """Vertex for Winged Edge Data Structure"""
    def __init__(self, x,y, edge=None):
        super(Vertex, self).__init__()
        self.x= x
        self.y =y
        self.edge = edge # one incident edge for the vertex
    def __str__(self):
        return "(%f, %f)"%(self.x, self.y)

class Edge(object):
    """Edge for Winged Edge Data Structure"""
    def __init__(self, startV, endV, left=None, right=None,
                pl=None, sl=None, pr=None, sr=None, name=None):
        super(Edge, self).__init__()

        self.start = startV  # start vertex
        self.end = endV      # end vertex
        self.left = left     # left face
        self.right = right   # right face
        self.pl = pl         # preceding edge for cw traversal of left face
        self.sl = sl         # successor edge for cw traversal of left face
        self.pr = pr         # preceding edge for cw traversal of right face
        self.sr = sr         # successor edge for cw traversal of right face 
        self.name = name

    def __str__(self):
        if not self.name:
            self.name = 'Edge'
        return "%s: (%f,%f)--(%f,%f)"%(self.name, self.start.x, self.start.y, self.end.x,
                self.end.y) 
        
class Face(object):
    """Face for Winged Edge Data Structure"""
    def __init__(self, nodes, edge=None):
        super(Face, self).__init__()
        self.nodes = nodes # nodes/vertices defining face
        self.edge = edge # one incident edge for the face

        if self.nodes[0] != self.nodes[-1]:
            self.nodes.append(self.nodes[0]) # put in closed form

    def __str__(self):
        n = len(self.nodes)
        nv = [ "(%f,%f)"%(v.x,v.y) for v in self.nodes]
        return "--".join(nv)

def face_boundary(face):
    """Clockwise traversal around face edges

    Arguments
    --------
    face: face instance

    Returns
    ------
    edges: list of edges on face boundary ordered clockwise

    """
    l0 = face.edge
    l = l0
    edges = []
    traversing = True
    while traversing:
        edges.append(l)
        r = l.right
        if r == face:
            l = l.sr
        else:
            l = l.sl
        if l == l0:
            traversing = False
    return edges


def incident_cw_edges_node(node):
    """Clockwise traversal of edges incident with node

    Arguments
    ---------

    node: Vertex instance

    Returns
    ------
    edges: list of edges that are cw incident with node

    """
    l0 = node.edge
    l = l0
    edges = []
    traversing = True
    while traversing:
        edges.append(l)
        v = l.start
        if v == node:
            l = l.pr
        else:
            l = l.pl
        #print l0, l
        if l0 == l:
            traversing = False
        #raw_input('here')
    return edges


        
if __name__ == '__main__':

    # example from figure 3.19 of okabe
    # omitting 1-3 link to ensure planarity

    import networkx as nx
    import numpy as np

    V = [ (0,0), (1,1), (2,0), (1,-1), (2,-1) ] 
    E = [ (1,2,3), (0,2), (1,0,3), (0,2,4), (3,) ]

    P = np.array(V)

    G = nx.Graph()
    for i,d in enumerate(E):
        for j in d:
            G.add_edge(i,j)


    # Alternative implementation of WED

    """Simple network example

    A a B b C m J
    c 1 d 2 e
    D f E g F
    h 3 i 4 j
    G k H l I

    Where upper case letters are Nodes/Vertices, lower case letters are edges,
    and integers are face ids.
    
    There are four faces 1-4, but one external face 0 (implied)
    """



    vertices = {}
    vertices['A'] = Vertex(0.,2.)
    vertices['B'] = Vertex(1.,2.)
    vertices['C'] = Vertex(2.,2.)
    vertices['D'] = Vertex(0.,1.)
    vertices['E'] = Vertex(1.,1.)
    vertices['F'] = Vertex(2.,1.)
    vertices['G'] = Vertex(0.,0.)
    vertices['H'] = Vertex(1.,0.)
    vertices['I'] = Vertex(2.,0.)
    vertices['J'] = Vertex(3.,2.)



    edges = {}
    edata = [ ('a', 'A', 'B'),
              ('b', 'B', 'C'),
              ('c', 'A', 'D'),
              ('d', 'E', 'B'),
              ('e', 'C', 'F'),
              ('f', 'D', 'E'),
              ('g', 'E', 'F'),
              ('h', 'D', 'G'),
              ('i', 'H', 'E'),
              ('j', 'F', 'I'),
              ('k', 'G', 'H'),
              ('l', 'I', 'H'),
              ('m', 'C', 'J')]

    for edge in edata:
        edges[edge[0]] = Edge(vertices[edge[1]], vertices[edge[2]])

    faces = {}
    fdata = [ ('A', 'B', 'E', 'D'),
              ('B', 'C', 'F', 'E'),
              ('D', 'E', 'H', 'G'),
              ('E', 'F', 'I', 'H') ]

    fe = [ 'c', 'd', 'f', 'j']

    for i, face in enumerate(fdata):
        i+=1
        coords = [ vertices[j] for j in face]
        faces[i] = Face(coords)
        faces[i].edge = edges[fe[i-1]]

    faces[0] = Face([0.,0.,0.0])
    faces[0].edge = edges['h']

    lrdata = [ (0,1),
               (0,2),
               (1,0),
               (1,2),
               (0,2),
               (1,3),
               (2,4),
               (3,0),
               (3,4),
               (0,4),
               (3,0),
               (0,4),
               (0,0)]
    ekeys = edges.keys()
    ekeys.sort()

    for i, lr in enumerate(lrdata):
        edges[ekeys[i]].left = faces[lr[0]]
        edges[ekeys[i]].right = faces[lr[1]]



    psdata = [ #node pre_left successor_left, pre_right, successor_right
            ('a', 'b', 'c', 'c', 'd'),
            ('b', 'm', 'a', 'd', 'e'),
            ('c', 'f', 'a', 'a', 'h'),
            ('d', 'a', 'f', 'g', 'b'),
            ('e', 'j', 'm', 'b', 'g'),
            ('f', 'd', 'c', 'h', 'i'),
            ('g', 'e', 'd', 'i', 'j'),
            ('h', 'k', 'f', 'c', 'k'),
            ('i', 'f', 'k', 'l', 'g'),
            ('j', 'l', 'e', 'g', 'l'),
            ('k', 'i', 'h', 'h', 'l'),
            ('l', 'k', 'j', 'j', 'i'),
            ('m', 'e', 'b', 'e', 'b') ]

    for pdata in psdata:
        e,pl,sl,pr,sr = pdata
        edges[e].pl = edges[pl]
        edges[e].sl = edges[sl]
        edges[e].pr = edges[pr] 
        edges[e].sr = edges[sr]
        edges[e].name = e

    n2e = [
            ('A', 'c'),
            ('B', 'b'),
            ('C', 'e'),
            ('D', 'f'),
            ('E', 'd'),
            ('F', 'g'),
            ('G', 'h'),
            ('H', 'k'),
            ('I', 'j'),
            ('J', 'm')]
    for node in n2e:
        v,e = node
        vertices[v].edge = edges[e]

    cv = 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', "I"
    for v in cv:
        icwe = incident_cw_edges_node(vertices[v])
        print "Node: ", v, "cw incident edges: "
        for e in icwe:
            print e


    for f in range(1,5):
        ecwf = face_boundary(faces[f])
        print "Face: ",f, " cw edges:"
        for e in ecwf:
            print e

