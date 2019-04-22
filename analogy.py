#!/usr/bin/env python3
import os.path
import sys
import heapq
import operator
import statistics as stat

import vpython

import analogy.vpython_drawings as vpython_drawings
import analogy.collision_detection.aabb_collision as aabb_col
import analogy.file_parsers as file_parsers
from analogy.mesh import AABB
from analogy.mapping import Mapping
import user_inputs

from analogy.storage import sqlitedb

picked_vpython_obj = None


def add_to_db(kb_db_name, obj_file_path):
    """
    Add knowledge about the target object manipulation to the database.

    Args:
        kb_db_name(str): The knowledge base database file name.
        obj_file_path(str): File path to the .obj file.
    """
    # create vpython scene that is used for graphical representation of a scene
    # for the user
    vpython_scene = vpython.canvas(
        title='',
        width=800,
        height=600,
        center=vpython.vector(0, 0, 0),
        background=vpython.color.black)

    # Draw XYZ axis in the scene
    vpython_drawings.draw_xyz_arrows(300.0)
    scene = file_parsers.read_obj_file(obj_file_path)

    # collision detection for each mesh in the scene
    min_distance = 3
    for mesh_1 in scene.values():
        for mesh_2 in scene.values():
            if mesh_1.name != mesh_2.name:
                aabb_collision = aabb_col.aabb_intersect(
                    mesh_1, mesh_2, min_distance=min_distance)
                if aabb_collision:
                    for surface in mesh_1.surfaces:
                        intersect = aabb_col.aabb_intersect_vertex(
                            mesh_2, surface.collider, min_distance=min_distance)
                        if intersect:
                            surface.collided_objects[mesh_2.name] = True
                            surface.collision = True
                            mesh_1.collision = True
                            mesh_1.collided_objects[mesh_2.name] = True
        for side, surfaces in mesh_1.aabb.closest_surfaces.items():
            counter = 0
            for surface in surfaces:
                if surface.collision:
                    counter += 1
            if counter == len(surfaces):
                mesh_1.aabb.collided_sides[side] = 2
            elif counter > 0 and counter < len(surfaces):
                mesh_1.aabb.collided_sides[side] = 1

            # print(mesh_1.name, side, mesh_1.aabb.collided_sides[side])

    # vpython_drawings.draw_colliders(mesh_list=scene.values())
    vpython_drawings.draw_aabb_colliders(mesh_list=scene.values())
    # vpython_drawings.draw_mesh(mesh_list=scene.values())
    vpython_drawings.draw_aabb(mesh_list=scene.values(), opacity=0.4)

    # select target object
    picked_vpython_obj = user_inputs.select_object(vpython_scene)
    picked_obj = scene[picked_vpython_obj.name[:-5]]

    # get manipulation points and vectors
    user_inputs.get_point(vpython_scene, picked_obj, picked_vpython_obj, 'push')
    user_inputs.get_vector(vpython_scene, picked_obj, picked_vpython_obj,
                           'push')

    user_inputs.get_point(vpython_scene, picked_obj, picked_vpython_obj, 'pull')
    user_inputs.get_vector(vpython_scene, picked_obj, picked_vpython_obj,
                           'pull')

    user_inputs.get_point(vpython_scene, picked_obj, picked_vpython_obj,
                          'spatula')
    user_inputs.get_vector(vpython_scene, picked_obj, picked_vpython_obj,
                           'spatula')

    # save the scene to a file and DB
    db = sqlitedb.sqlitedb(name=kb_db_name)
    db.create_db()  # create tables if not exist
    file_path_list = obj_file_path.split('/')
    file_name_obj = file_path_list[-1]
    file_name_list = file_name_obj.split('.')
    scene_name = file_name_list[0]
    db.save_scene(scene, scene_name, picked_obj)
    db.conn.close()
    print('Done')


def solve_scene(kb_db_name, obj_file_path):
    """
    Solve manipulation for the target object in the scene using analogy.

    Args:
        kb_db_name(str): The knowledge base database file name.
        obj_file_path(str): File path to the .obj file.
    """
    # create vpython scene that is used for graphical representation of a scene
    # for the user
    vpython_scene = vpython.canvas(
        title='',
        width=800,
        height=600,
        center=vpython.vector(0, 0, 0),
        background=vpython.color.black)

    # Draw XYZ axis in the scene
    vpython_drawings.draw_xyz_arrows(300.0)
    scene = file_parsers.read_obj_file(obj_file_path)

    # collision detection for each mesh in the scene
    min_distance = 3
    for mesh_1 in scene.values():
        for mesh_2 in scene.values():
            if mesh_1.name != mesh_2.name:
                aabb_collision = aabb_col.aabb_intersect(
                    mesh_1, mesh_2, min_distance=min_distance)
                if aabb_collision:
                    for surface in mesh_1.surfaces:
                        intersect = aabb_col.aabb_intersect_vertex(
                            mesh_2, surface.collider, min_distance=min_distance)
                        if intersect:
                            surface.collided_objects[mesh_2.name] = True
                            surface.collision = True
                            mesh_1.collision = True
                            mesh_1.collided_objects[mesh_2.name] = True
        for side, surfaces in mesh_1.aabb.closest_surfaces.items():
            counter = 0
            for surface in surfaces:
                if surface.collision:
                    counter += 1
            if counter == len(surfaces):
                mesh_1.aabb.collided_sides[side] = 2
            elif counter > 0 and counter < len(surfaces):
                mesh_1.aabb.collided_sides[side] = 1

    # vpython_drawings.draw_colliders(mesh_list=scene.values())
    vpython_drawings.draw_aabb_colliders(mesh_list=scene.values())
    # vpython_drawings.draw_mesh(mesh_list=scene.values())
    vpython_drawings.draw_aabb(mesh_list=scene.values(), opacity=0.4)

    # select target object
    picked_vpython_obj = user_inputs.select_object(vpython_scene)
    picked_obj = scene[picked_vpython_obj.name[:-5]]

    # get aabbs from KB
    db = sqlitedb.sqlitedb(name=kb_db_name)
    db_aabbs = db.select_all_aabbs()

    # rebuild aabb from db as an AABB object
    aabbs = {}
    for db_aabb in db_aabbs:
        # get positions of manipulation points and vector forces from DB
        pos = db.select_position_id(db_aabb[2])
        push_point = db.select_position_id(
            int(db.select_push_point_id(int(db_aabb[3]))[1]))
        push_vec = db.select_push_vec_id(int(db_aabb[4]))
        pull_point = db.select_position_id(
            int(db.select_pull_point_id(int(db_aabb[5]))[1]))
        pull_vec = db.select_pull_vec_id(int(db_aabb[6]))
        spatula_point = db.select_position_id(
            int(db.select_spatula_point_id(int(db_aabb[7]))[1]))
        spatula_vec = db.select_spatula_vec_id(int(db_aabb[8]))
        # Create AABB object and assign collided sides
        aabb = AABB([pos[1], pos[2], pos[3]],
                    [db_aabb[9], db_aabb[10], db_aabb[11]])
        aabb.collided_sides['top'] = db_aabb[12]
        aabb.collided_sides['bottom'] = db_aabb[13]
        aabb.collided_sides['front'] = db_aabb[14]
        aabb.collided_sides['back'] = db_aabb[15]
        aabb.collided_sides['right'] = db_aabb[16]
        aabb.collided_sides['left'] = db_aabb[17]
        # assign manipulation points and force vectors for the AABB object
        if push_point[1] is not None:
            aabb.manipulation_points['push'] = [
                float(push_point[1]),
                float(push_point[2]),
                float(push_point[3])
            ]
            aabb.manipulation_vectors['push'] = [
                int(push_vec[1]),
                int(push_vec[2]),
                int(push_vec[3])
            ]
        else:
            aabb.manipulation_points['push'] = None
            aabb.manipulation_vectors['push'] = None
        if pull_point[1] is not None:
            aabb.manipulation_points['pull'] = [
                float(pull_point[1]),
                float(pull_point[2]),
                float(pull_point[3])
            ]
            aabb.manipulation_vectors['pull'] = [
                int(pull_vec[1]),
                int(pull_vec[2]),
                int(pull_vec[3])
            ]
        else:
            aabb.manipulation_points['pull'] = None
            aabb.manipulation_vectors['pull'] = None
        if spatula_point[1] is not None:
            aabb.manipulation_points['spatula'] = [
                float(spatula_point[1]),
                float(spatula_point[2]),
                float(spatula_point[3])
            ]
            aabb.manipulation_vectors['spatula'] = [
                int(spatula_vec[1]),
                int(spatula_vec[2]),
                int(spatula_vec[3])
            ]
        else:
            aabb.manipulation_points['spatula'] = None
            aabb.manipulation_vectors['spatula'] = None
        aabbs[db_aabb[0]] = aabb

    # get all mappings and their scores. Sort them based on highest score
    analogy_mapping = Mapping()
    mappings_scores = []
    for aabb_id, aabb in aabbs.items():
        new_aabb_scores = analogy_mapping.get_mappings_score(
            target_aabb=picked_obj.aabb, source_aabb=aabb)
        # save only top 3 rotation sequences based on highest score
        top_3_scores = heapq.nlargest(
            3, new_aabb_scores, key=operator.itemgetter(0))
        # The result is saved as tuple in a form
        # (aabb_id, top score from all 3, list of best 3 rotation sequences with their scores)
        mappings_scores.append((aabb_id, top_3_scores[0][0], top_3_scores))
    # sort the mapping scores based on the top scores
    mappings_scores = sorted(
        mappings_scores, key=operator.itemgetter(1), reverse=True)

    # print out info about best mapping
    print(':' * 120)
    for aabb_mapping in mappings_scores:
        print('=' * 120)
        print('aabb id:', aabb_mapping[0], 'scene:',
              db.select_aabb_id(aabb_mapping[0])[1])
        print('max score for the AABB:', aabb_mapping[1])
        for score in aabb_mapping[2]:
            print('-' * 120)
            print('score:', score[0], '\nsequence:', score[1], '\nmapping:',
                  analogy_mapping.all_permutations[score[1]])

    # rotate vectors based on the permutation sequence
    best_sequence = mappings_scores[0][2][0][1]
    rotated_manipulation_vec = {}
    for operation, vec in aabbs[mappings_scores[0]
                                [0]].manipulation_vectors.items():
        if vec is not None:
            vpython_vec = vpython.vec(vec[0], vec[1], vec[2])
            # best_sequence not reversed because we want to rotate the manipulation vectors from
            # source scenario to target one. Best sequence is from target to source.
            # For example (x,y) means first transform y and then x.
            # Since we want to go backwards it is already in the correct order.
            for rotation in best_sequence:
                if rotation == 'x':
                    vpython_vec = vpython.rotate(
                        vpython_vec,
                        angle=vpython.radians(90),
                        axis=vpython.vec(1, 0, 0))
                elif rotation == 'y':
                    vpython_vec = vpython.rotate(
                        vpython_vec,
                        angle=vpython.radians(90),
                        axis=vpython.vec(0, 1, 0))
            rotated_manipulation_vec[operation] = [
                vpython_vec.x, vpython_vec.y, vpython_vec.z
            ]
        else:
            rotated_manipulation_vec[operation] = [None, None, None]
        picked_obj.aabb.manipulation_vectors = rotated_manipulation_vec

    # get dict that maps surfaces from target to source
    # For example 'top':'left' top surface is going to be left to map to source
    mapping_sides = analogy_mapping.all_permutations[best_sequence]
    aabb_half_size = aabbs[mappings_scores[0][0]].half_size
    aabb_pos = aabbs[mappings_scores[0][0]].pos
    # determine x,y,z ratios for scaling factor that is applied
    # for manipulation points positions. It is important to determine which
    # rotation took place in order to determine correct scaling ratios.
    x_ratio = 0
    y_ratio = 0
    z_ratio = 0
    if (mapping_sides['top'] == 'top' or mapping_sides['top'] == 'bottom') and (
            mapping_sides['front'] == 'front' or
            mapping_sides['front'] == 'back'):
        x_ratio = picked_obj.aabb.half_size[0] / aabb_half_size[0]
        y_ratio = picked_obj.aabb.half_size[1] / aabb_half_size[1]
        z_ratio = picked_obj.aabb.half_size[2] / aabb_half_size[2]

    elif (mapping_sides['top'] == 'top' or mapping_sides['top'] == 'bottom'
         ) and (mapping_sides['front'] == 'right' or
                mapping_sides['front'] == 'left'):
        x_ratio = picked_obj.aabb.half_size[2] / aabb_half_size[0]
        y_ratio = picked_obj.aabb.half_size[1] / aabb_half_size[1]
        z_ratio = picked_obj.aabb.half_size[0] / aabb_half_size[2]
    elif (mapping_sides['top'] == 'left' or mapping_sides['top'] == 'right'
         ) and (mapping_sides['front'] == 'front' or
                mapping_sides['front'] == 'back'):
        x_ratio = picked_obj.aabb.half_size[1] / aabb_half_size[0]
        y_ratio = picked_obj.aabb.half_size[0] / aabb_half_size[1]
        z_ratio = picked_obj.aabb.half_size[2] / aabb_half_size[2]
    elif (mapping_sides['top'] == 'left' or mapping_sides['top'] == 'right'
         ) and (mapping_sides['front'] == 'top' or
                mapping_sides['front'] == 'bottom'):
        x_ratio = picked_obj.aabb.half_size[1] / aabb_half_size[0]
        y_ratio = picked_obj.aabb.half_size[2] / aabb_half_size[1]
        z_ratio = picked_obj.aabb.half_size[0] / aabb_half_size[2]
    elif (mapping_sides['top'] == 'front' or mapping_sides['top'] == 'back'
         ) and (mapping_sides['front'] == 'bottom' or
                mapping_sides['front'] == 'top'):
        x_ratio = picked_obj.aabb.half_size[0] / aabb_half_size[0]
        y_ratio = picked_obj.aabb.half_size[2] / aabb_half_size[1]
        z_ratio = picked_obj.aabb.half_size[1] / aabb_half_size[2]
    elif (mapping_sides['top'] == 'front' or mapping_sides['top'] == 'back'
         ) and (mapping_sides['front'] == 'right' or
                mapping_sides['front'] == 'left'):
        x_ratio = picked_obj.aabb.half_size[2] / aabb_half_size[0]
        y_ratio = picked_obj.aabb.half_size[0] / aabb_half_size[1]
        z_ratio = picked_obj.aabb.half_size[1] / aabb_half_size[2]
    else:
        raise ValueError

    rotated_manipulation_points = {}
    # iterate through all manipulation points and rotate them based on the best sequence
    for operation, pos in aabbs[mappings_scores[0]
                                [0]].manipulation_points.items():
        if pos is not None:
            # calculate relative position from manipulation point to centre of AABB
            relative_pos = [
                pos[0] - aabb_pos[0], pos[1] - aabb_pos[1], pos[2] - aabb_pos[2]
            ]
            # Scale the position to match the size of our target AABB
            scaled_relative_pos = [
                relative_pos[0] * x_ratio, relative_pos[1] * y_ratio,
                relative_pos[2] * z_ratio
            ]
            # create vpython vec that is used in rotation method
            vpython_vec = vpython.vec(scaled_relative_pos[0],
                                      scaled_relative_pos[1],
                                      scaled_relative_pos[2])
            # rotate the manipulation points positions from source to target scene
            for rotation in best_sequence:
                if rotation == 'x':
                    vpython_vec = vpython.rotate(
                        vpython_vec,
                        angle=vpython.radians(90),
                        axis=vpython.vec(1, 0, 0))
                elif rotation == 'y':
                    vpython_vec = vpython.rotate(
                        vpython_vec,
                        angle=vpython.radians(90),
                        axis=vpython.vec(0, 1, 0))
            # Shift the manipulation point position from relative pos to absolute pos in the scene
            scaled__rotated_abs_pos = [
                vpython_vec.x + picked_obj.aabb.pos[0],
                vpython_vec.y + picked_obj.aabb.pos[1],
                vpython_vec.z + picked_obj.aabb.pos[2]
            ]
            rotated_manipulation_points[operation] = scaled__rotated_abs_pos

            # Draw rotated manipulation points and vectors on the screen
            radius = stat.mean(picked_obj.aabb.half_size) / 10
            if operation == 'push':
                color = vpython.color.cyan
            elif operation == 'pull':
                color = vpython.color.purple
            else:
                color = vpython.color.orange
            vpython_drawings.draw_point(
                rotated_manipulation_points[operation], radius, color=color)
            vector_length = stat.mean(picked_obj.aabb.half_size)
            vpython_drawings.draw_arrow(
                rotated_manipulation_points[operation],
                picked_obj.aabb.manipulation_vectors[operation],
                vector_length,
                color=color)
        else:
            rotated_manipulation_points[operation] = [None, None, None]
        # assig the calculated manipulation points to the target AABB
        picked_obj.aabb.manipulation_points = rotated_manipulation_points

    # save it to the DB if it is correct.
    correct_result = input(
        'Are these manipulation points and vectors correct? Yes/No: ')
    if correct_result.lower() == 'y' or correct_result.lower() == 'yes':
        file_path_list = obj_file_path.split('/')
        file_name_obj = file_path_list[-1]
        file_name_list = file_name_obj.split('.')
        scene_name = file_name_list[0]
        db.save_scene(scene, scene_name, picked_obj)
        print('Successfully Saved in knowledge base DB.')
    else:
        print('This is not going to be saved in the knowledge base DB.')

    print('Done')
    # close DB
    db.conn.close()


def main():
    if len(sys.argv) != 4:
        raise ValueError('''
            First arg: task [add || solve]
            \nSecond: path to .obj file
            \nThird: KB DB file path.
            ''')
    if not (sys.argv[1].lower() == 'add' or sys.argv[1].lower() == 'solve'):
        raise ValueError('Supports only "add" or "solve" tasks.')
    if not (sys.argv[2].endswith('.obj')):
        raise TypeError('Supports only .obj files.')
    if not (sys.argv[3].endswith('.db') or sys.argv[3].endswith('.sqlite')):
        raise TypeError('Supports only sqlite files as a database for KB.')
    kb_db_name = sys.argv[3]
    if sys.argv[1].lower() == 'add':
        obj_file_path = sys.argv[2]
        add_to_db(kb_db_name=kb_db_name, obj_file_path=obj_file_path)

    elif sys.argv[1].lower() == 'solve':
        obj_file_path = sys.argv[2]
        solve_scene(kb_db_name=kb_db_name, obj_file_path=obj_file_path)


if __name__ == '__main__':
    main()
