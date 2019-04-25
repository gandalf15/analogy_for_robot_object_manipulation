class Mesh:
    """
    Mesh is a representation of a mesh in memory

    Attributes:
        name(str): Name of the mesh
        surfaces(list): A list of Surfaces that belong to the mesh instance.
        collision(bool): If the AABB has collision it is True.
        collided_objects(dict): Dict of all mesh names that the mesh collides
            with.
        aabb(AABB): Axis Aligned Bounding Box for the mesh
        color(list): A color of the mesh in RGB. Min value is 0.0 and max is 1.0.
            Default value is white that is [1.0, 1.0, 1.0].
    """

    def __init__(self):
        """Init Mesh"""
        self.name = ''
        self.surfaces = []
        self.collision = False
        self.collided_objects = {}
        self.aabb = AABB([], [])
        self.color = [1.0, 1.0, 1.0]

    @property
    def set_name(self, name):
        self.name = name

    @property
    def set_surfaces(self, surfaces):
        self.surfaces = surfaces

    @property
    def set_color(self, color):
        self.color = color

    @property
    def get_name(self):
        return self.name

    @property
    def get_surfaces(self):
        return self.surfaces

    @property
    def get_color(self):
        return self.color


class Surface:
    """
    Surface is a representation of a surface in memory 

    Attributes:
        vertices(list): A list of vertices that belong to the surface instance.
        collider(list): 3D space coordinates of the collider for the surface.
            It is the centroid of the surface.
        collision(bool): If the surface has a collision it is True.
        collided_objects(dict): Dict of all names of meshes that the surface
            collides with.
    """

    def __init__(self, vertices):
        """
        Init Surface
        
        Args:
            vertices(list): A list of vertices that belong to the surface instance.
        """
        self.vertices = vertices
        self.collider = []
        self.collision = False
        self.collided_objects = {}

    @property
    def set_vertices(self, vertices):
        self.vertices = vertices

    @property
    def set_collision(self, collision):
        self.collision = collision

    @property
    def set_collided_objects(self, collided_objects):
        self.collided_objects = collided_objects

    @property
    def get_vertices(self):
        return self.vertices

    @property
    def get_collision(self):
        return self.collision

    @property
    def get_collided_objects(self):
        return self.collided_objects


class Vertex:
    """
    Vertex is a representation of a vertex in memory 

    Attributes:
        pos(list): list of coordinates
    """

    def __init__(self, pos):
        """
        Init a new instance of Vertex

        Args:
            pos(list): list of coordinates
        """
        self.pos = pos


class AABB:
    """
    AABB is a representation of a Axis Aligned Bounding Box in memory.

    Attributes:
        pos(list): list of [x,y,z] coordinates
        half_size(list): size of the AABB / 2 along x,y,z axis 
            [width/2, height/2, depth/2]
        manipulation_points(dict): Dict of all known manipulation points.
        manipulation_vectors(dict): Dict of all known manipulation vectors.
        closest_surfaces(dict): Dict of 'side_name' and list of closest associated
            surfaces.
        collided_sides(dict): Dict of 'side_name' and encoding of collision.
            For eample, no collision = 0, partial collision = 1, full = 2.
        color(list): A color of the mesh in RGB. Min value is 0.0 and max is 1.0.
    """

    def __init__(self, pos, half_size):
        """
        Init a new instance of Vertex

        Args:
            pos(list): list of [x,y,z] coordinates
            half_size(list): size of the AABB / 2 
                along x,y,z axis [width/2, height/2, depth/2]
        """
        self.pos = pos
        self.half_size = half_size
        self.manipulation_points = {}
        self.manipulation_vectors = {}
        self.closest_surfaces = {}
        self.collided_sides = {}
        # init the dict with 0 value that means no collision
        self.collided_sides['top'] = 0
        self.collided_sides['bottom'] = 0
        self.collided_sides['front'] = 0
        self.collided_sides['back'] = 0
        self.collided_sides['right'] = 0
        self.collided_sides['left'] = 0
        self.color = []

    @property
    def set_pos(self, pos):
        self.pos = pos

    @property
    def set_half_size(self, half_size):
        self.half_size = half_size

    @property
    def get_aabb_pos(self):
        return self.aabb_pos

    @property
    def get_half_size(self):
        return self.half_size