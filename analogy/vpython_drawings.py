import vpython


def draw_mesh(mesh_list, opacity=0.5):
    """
    Draw meshes to the scene.

    Args:
        mesh_list(list): A list of Mesh objects that should be drawn on the scene.
        opacity(float): Optional. Opacity of the mesh objects.
    Returns:
        A list of vpython.compound objects that represent the meshes.
    """
    compounds = {}
    for mesh in mesh_list:
        surfaces = []
        for surface in mesh.surfaces:
            vertices = []
            for vertex in surface.vertices:
                v_pos = vertex.pos
                v = vpython.vertex(
                    pos=vpython.vec(v_pos[0], v_pos[1], v_pos[2]))
                v.opacity = opacity
                if surface.collision:
                    v.color = vpython.vec(1.0 - mesh.color[0],
                                          1.0 - mesh.color[1],
                                          1.0 - mesh.color[2])
                else:
                    v.color = vpython.vec(mesh.color[0], mesh.color[1],
                                          mesh.color[2])
                vertices.append(v)
            surfaces.append(
                vpython.triangle(vs=[vertices[0], vertices[1], vertices[2]]))
        compounds[mesh.name] = vpython.compound(surfaces)
        # compounds[mesh.name].pickable = False
        compounds[mesh.name].name = mesh.name
    return compounds


def draw_colliders(mesh_list, opacity=1.0, radius=1.0):
    """
    Draw colliders to the scene.

    Args:
        mesh_list(list): A list of Mesh objects which colliders should be drawn
            on the scene.
        opacity(float): Optional. Opacity of the colliders.
        radius(float): Radius of the collider spheres. Influence only how they
            are displayed.
    Returns:
        A dict of colliders where key is the name of the mesh object and value
        is a list of vpython.sphere objects that represents the colliders.
    """
    colliders = {}
    for mesh in mesh_list:
        counter = 0
        colliders[mesh.name] = []
        for surface in mesh.surfaces:
            colliders[mesh.name].append(
                vpython.sphere(
                    pos=vpython.vec(surface.collider[0], surface.collider[1],
                                    surface.collider[2]),
                    radius=radius))
            colliders[mesh.name][-1].opacity = opacity
            if surface.collision:
                colliders[mesh.name][-1].color = vpython.color.red
            colliders[
                mesh.name][-1].name = mesh.name + '_collider_' + str(counter)
            counter += 1
    return colliders


def draw_aabb_colliders(mesh_list, opacity=1.0, radius=1.0):
    """
    Draw AABB colliders to the scene.

    Args:
        mesh_list(list): A list of Mesh objects which AABB colliders that should
            be drawn on the scene.
        opacity(float): Optional. Opacity of the colliders.
        radius(float): Radius of the collider spheres. Influence only how they
            are displayed.
    Returns:
        A dict of colliders where key is the name of the mesh object and value
        is a list of vpython.sphere objects that represents the colliders.
    """
    colliders = {}
    for mesh in mesh_list:
        counter = 0
        colliders[mesh.name] = []
        for surfaces in mesh.aabb.closest_surfaces.values():
            for surface in surfaces:
                colliders[mesh.name].append(
                    vpython.sphere(
                        pos=vpython.vec(surface.collider[0],
                                        surface.collider[1],
                                        surface.collider[2]),
                        radius=radius))
                colliders[mesh.name][-1].opacity = opacity
                if surface.collision:
                    colliders[mesh.name][-1].color = vpython.color.red
                colliders[mesh.name][
                    -1].name = mesh.name + '_aabb_collider_' + str(counter)
                counter += 1
    return colliders


def draw_aabb(mesh_list, opacity=0.2):
    """
    Draws the AABB of a mesh.

    Args:
        mesh_list(list): A list of Mesh objects which AABB that should be
            drawn on the scene.
        opacity(float): Optional. Opacity of the AABB.
    Returns:
        A dict of vpython.box objects that represents the AABBs on the scene.
        key is the mesh name and the value is the vpython.box.
    """
    aabbs = {}
    for mesh in mesh_list:
        aabbs[mesh.name] = vpython.box(
            pos=vpython.vec(
                mesh.aabb.pos[0],
                mesh.aabb.pos[1],
                mesh.aabb.pos[2],
            ),
            size=vpython.vec(
                mesh.aabb.half_size[0] * 2,
                mesh.aabb.half_size[1] * 2,
                mesh.aabb.half_size[2] * 2,
            ))
        aabbs[mesh.name].opacity = opacity
        aabbs[mesh.name].color = vpython.vec(
            mesh.aabb.color[0], mesh.aabb.color[1], mesh.aabb.color[2])
        aabbs[mesh.name].name = mesh.name + '_aabb'
    return aabbs


def draw_xyz_arrows(pointer_size: int):
    """
    Draws 3 arrows along X, Y and Z axis.

    Args:
        pointer_size(int): Size of the arrowns on the scene.
    Returns:
        A list of vpython.arrow objects that represents the arrows on the scene.
    """
    pointers = []
    pointer_x = vpython.arrow(
        pos=vpython.vec(-(pointer_size / 2), 0, 0),
        axis=vpython.vec(pointer_size, 0, 0),
        shaftwidth=1,
        color=vpython.color.red,
        opacity=0.3)
    pointer_y = vpython.arrow(
        pos=vpython.vec(0, -(pointer_size / 2), 0),
        axis=vpython.vec(0, pointer_size, 0),
        shaftwidth=1,
        color=vpython.color.green,
        opacity=0.3)
    pointer_z = vpython.arrow(
        pos=vpython.vec(0, 0, -(pointer_size / 2)),
        axis=vpython.vec(0, 0, pointer_size),
        shaftwidth=1,
        color=vpython.color.yellow,
        opacity=0.3)
    pointers.append(pointer_x)
    pointers.append(pointer_y)
    pointers.append(pointer_z)
    return pointers


def draw_point(pos, radius, color=vpython.color.cyan):
    """
    Draws a point (sphere) on the scene.

    Args:
        pos(list): [x,y,z] 3D space coordinates of the sphere.
        radius(float): Radius of the spheres.
        color(vpython.color): Optional. Color of the sphere.

    Returns:
        vpython.sphere that represents the point on the scene.
    """
    point_pos = vpython.vec(pos[0], pos[1], pos[2])
    point_color = color
    return vpython.sphere(pos=point_pos, radius=radius, color=point_color)


def draw_arrow(pos, axis, length, color=vpython.color.cyan):
    """
    Draws an arrow o the scene

    Args:
        pos(list): [x,y,z] 3D space coordinates of the origin.
        axis(list): [x,y,z] space vector that describes the arrow.
        length(float): length of the arrow on the scene.
        color(vpython.color): Optional. Color of the arrow.

    Returns:
        vpython.arrow that represents the arrow on the scene.
    """
    arrow_pos = vpython.vec(pos[0], pos[1], pos[2])
    arrow_axis = vpython.vec(axis[0], axis[1], axis[2])
    arrow_color = color
    return vpython.arrow(
        pos=arrow_pos, axis=arrow_axis, length=length, color=arrow_color)
