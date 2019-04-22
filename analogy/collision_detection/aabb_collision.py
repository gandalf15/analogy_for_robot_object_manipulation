def aabb_intersect(mesh_1, mesh_2, min_distance):
    """
    Checks if two Mesh object intersect.

    Args:
        mesh_1(Mesh): mesh 1 that we wish to check for collision with mesh 2
        mesh_2(Mesh): mesh 2 that we wish to check for collision with mesh 1
        min_distance(float): minimum distance (no units) that has to be between
            the meshes. 

    Return:
        True if the meshes intersect.
    """
    # check X axis
    if abs(mesh_1.aabb.pos[0] - mesh_2.aabb.pos[0]) < (
            mesh_1.aabb.half_size[0] + mesh_2.aabb.half_size[0]) + min_distance:
        # check Y axis
        if abs(mesh_1.aabb.pos[1] -
               mesh_2.aabb.pos[1]) < (mesh_1.aabb.half_size[1] +
                                      mesh_2.aabb.half_size[1]) + min_distance:
            # check Z axis
            if abs(mesh_1.aabb.pos[2] - mesh_2.aabb.pos[2]) < (
                    mesh_1.aabb.half_size[2] +
                    mesh_2.aabb.half_size[2]) + min_distance:
                return True
    return False


def aabb_intersect_vertex(mesh, vertex, min_distance):
    """
    Checks if a vertex intersects with AABB in 3D space.

    Args:
        mesh(Mesh): A Mesh object that we wish to check if it intersects with
            the vertex.
        min_distance(float):minimum distance (no units) that has to be between
            the mesh and the vertex.

    Returns:
        True if the vertex intersects with the AABB.
    """
    # AABB (Axis Aligned Bounding Box)
    # check X axis
    if abs(mesh.aabb.pos[0] - vertex[0]) < (
        (mesh.aabb.half_size[0]) + min_distance):
        # check Y axis
        if abs(mesh.aabb.pos[1] - vertex[1]) < (
            (mesh.aabb.half_size[1]) + min_distance):
            # check Z axis
            if abs(mesh.aabb.pos[2] - vertex[2]) < (
                (mesh.aabb.half_size[2]) + min_distance):
                return True
    return False