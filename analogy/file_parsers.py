import os
from analogy.mesh import Mesh
from analogy.mesh import Surface
from analogy.mesh import Vertex
import statistics as stat


def read_obj_file(obj_file_path):
    """
    Reads OBJ file, creates Mesh object for each mesh in the file. Also, while
    parsing the file it calculates and creates AABB.

    Args:
        obj_file_path(str): File path to the .obj file.

    Returns:
        A dict of Mest objects where the key is the name of the mesh and value
            is Mesh object.
    """
    # read obj file
    with open(obj_file_path, 'r') as f:
        obj_lines = f.read().split('\n')

    # try to read mtl file if exists
    mtl_file_name = obj_file_path.replace('.obj', '.mtl')
    mtl_colors = {}
    if os.path.isfile(mtl_file_name):
        with open(mtl_file_name, 'r') as f:
            mtl_lines = f.read().split('\n')

        i = 0
        while i < len(mtl_lines):
            if mtl_lines[i].startswith('newmtl'):
                new_mtl_name = mtl_lines[i][7:]
                i += 1
                c = mtl_lines[i].split(' ')
                mtl_colors[new_mtl_name] = (float(c[1]), float(c[2]),
                                            float(c[3]))
            i += 1

    i = 0
    objects = {}
    all_vertices = []
    while i < len(obj_lines):
        new_obj_line = obj_lines[i]
        if new_obj_line != '' and not new_obj_line.startswith('#'):
            if new_obj_line.startswith('o '):
                new_mesh = Mesh()
                new_mesh.name = new_obj_line[2:]
                # we have a new object
                i += 1
                min_max_x_vertices = [float('+Infinity'), float('-Infinity')]
                min_max_y_vertices = [float('+Infinity'), float('-Infinity')]
                min_max_z_vertices = [float('+Infinity'), float('-Infinity')]
                while obj_lines[i].startswith('v '):
                    # while reading all vertices, find Axial Aligned bounding box for the object.
                    v = obj_lines[i][2:].split()
                    x = float(v[0])
                    min_max_x_vertices[0] = min(min_max_x_vertices[0], x)
                    min_max_x_vertices[1] = max(min_max_x_vertices[1], x)
                    y = float(v[1])
                    min_max_y_vertices[0] = min(min_max_y_vertices[0], y)
                    min_max_y_vertices[1] = max(min_max_y_vertices[1], y)
                    z = float(v[2])
                    min_max_z_vertices[0] = min(min_max_z_vertices[0], z)
                    min_max_z_vertices[1] = max(min_max_z_vertices[1], z)
                    all_vertices.append(Vertex([x, y, z]))
                    i += 1
                # print('min_max x y z:', min_max_x_vertices, min_max_y_vertices,
                #       min_max_z_vertices)
                new_aabb_size_x = abs(min_max_x_vertices[0] -
                                      min_max_x_vertices[1]) / 2
                new_aabb_size_y = abs(min_max_y_vertices[0] -
                                      min_max_y_vertices[1]) / 2
                new_aabb_size_z = abs(min_max_z_vertices[0] -
                                      min_max_z_vertices[1]) / 2
                new_mesh.aabb.half_size = [
                    new_aabb_size_x, new_aabb_size_y, new_aabb_size_z
                ]
                new_aabb_pos_x = stat.mean(min_max_x_vertices)
                new_aabb_pos_y = stat.mean(min_max_y_vertices)
                new_aabb_pos_z = stat.mean(min_max_z_vertices)
                new_mesh.aabb.pos = [
                    new_aabb_pos_x, new_aabb_pos_y, new_aabb_pos_z
                ]
                while obj_lines[i] == '' or obj_lines[i].startswith('#'):
                    i += 1
                if obj_lines[i].startswith('usemtl'):
                    if not mtl_colors:
                        raise ValueError(
                            "mtl color specified but mtl file does not exist.")
                    c = mtl_colors[obj_lines[i][7:]]
                    new_mesh.color = [float(c[0]), float(c[1]), float(c[2])]
                    new_mesh.aabb.color = [
                        float(c[0]), float(c[1]),
                        float(c[2])
                    ]
                    i += 1
                # we have a surface
                faces = []  # triangles
                while obj_lines[i].startswith('f '):
                    t = obj_lines[i][2:].split()
                    new_mesh.surfaces.append(
                        Surface([
                            all_vertices[int(t[0]) - 1],
                            all_vertices[int(t[1]) - 1],
                            all_vertices[int(t[2]) - 1]
                        ]))
                    surface_vertices = [
                        all_vertices[int(t[0]) - 1],
                        all_vertices[int(t[1]) - 1], all_vertices[int(t[2]) - 1]
                    ]
                    centroid = [.0, .0, .0]
                    for vertex in surface_vertices:
                        centroid[0] += vertex.pos[0]
                        centroid[1] += vertex.pos[1]
                        centroid[2] += vertex.pos[2]
                    for l in range(3):
                        centroid[l] /= len(surface_vertices)
                    new_mesh.surfaces[-1].collider = centroid
                    i += 1

                # find colliders associated with aabb sides
                aabb_surfaces = {}
                aabb_surfaces['top'] = [Surface([])]
                aabb_surfaces['top'][0].collider = [.0, float('-Infinity'), .0]
                aabb_surfaces['bottom'] = [Surface([])]
                aabb_surfaces['bottom'][0].collider = [
                    .0, float('+Infinity'), .0
                ]
                aabb_surfaces['front'] = [Surface([])]
                aabb_surfaces['front'][0].collider = [
                    .0, .0, float('-Infinity')
                ]
                aabb_surfaces['back'] = [Surface([])]
                aabb_surfaces['back'][0].collider = [.0, .0, float('+Infinity')]
                aabb_surfaces['right'] = [Surface([])]
                aabb_surfaces['right'][0].collider = [
                    float('-Infinity'),
                    .0,
                    .0,
                ]
                aabb_surfaces['left'] = [Surface([])]
                aabb_surfaces['left'][0].collider = [
                    float('+Infinity'),
                    .0,
                    .0,
                ]
                for surface in new_mesh.surfaces:
                    # check right collider (x coordinates)
                    if surface.collider[0] == aabb_surfaces['right'][
                            0].collider[0]:
                        aabb_surfaces['right'].append(surface)
                    elif surface.collider[0] > aabb_surfaces['right'][
                            0].collider[0]:
                        aabb_surfaces['right'] = [surface]

                    # check left collider (x coordinates)
                    if surface.collider[0] == aabb_surfaces['left'][0].collider[
                            0]:
                        aabb_surfaces['left'].append(surface)
                    elif surface.collider[0] < aabb_surfaces['left'][
                            0].collider[0]:
                        aabb_surfaces['left'] = [surface]

                    # check top collider (y coordinates)
                    if surface.collider[1] == aabb_surfaces['top'][0].collider[
                            1]:
                        aabb_surfaces['top'].append(surface)
                    elif surface.collider[1] > aabb_surfaces['top'][0].collider[
                            1]:
                        aabb_surfaces['top'] = [surface]

                    # check bottom collider (y coordinates)
                    if surface.collider[1] == aabb_surfaces['bottom'][
                            0].collider[1]:
                        aabb_surfaces['bottom'].append(surface)
                    elif surface.collider[1] < aabb_surfaces['bottom'][
                            0].collider[1]:
                        aabb_surfaces['bottom'] = [surface]

                    # check front collider (z coordinates)
                    if surface.collider[2] == aabb_surfaces['front'][
                            0].collider[2]:
                        aabb_surfaces['front'].append(surface)
                    elif surface.collider[2] > aabb_surfaces['front'][
                            0].collider[2]:
                        aabb_surfaces['front'] = [surface]

                    # check back collider (z coordinates)
                    if surface.collider[2] == aabb_surfaces['back'][0].collider[
                            2]:
                        aabb_surfaces['back'].append(surface)
                    elif surface.collider[2] < aabb_surfaces['back'][
                            0].collider[2]:
                        aabb_surfaces['back'] = [surface]
                new_mesh.aabb.closest_surfaces = aabb_surfaces
                objects[new_mesh.name] = new_mesh
        if i < len(obj_lines):
            i += 1

    return objects
