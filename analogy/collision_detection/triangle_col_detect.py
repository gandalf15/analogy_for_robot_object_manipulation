#!/usr/bin/env python3
import ctypes
import os

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
C_MOLLERS = ctypes.CDLL(os.path.join(CURRENT_PATH, 'build/mollers_tri_tri.so'))
C_DEVILLERS = ctypes.CDLL(
    os.path.join(CURRENT_PATH, 'build/devillers_tri_tri.so'))


def mollers_alg(tri_1, tri_2):
    """
    Wrapper for the mollers algorithm that is implemented in C.

    Args:
        tri_1(list): A list of 3 lists with space coordinates in 3D space.
        tri_2(list): A list of 3 lists with space coordinates in 3D space.

    Returns:
        True if two triangles collide.
    """
    global C_MOLLERS
    # int NoDivTriTriIsect(float V0[3],float V1[3],float V2[3],
    #                      float U0[3],float U1[3],float U2[3])
    three_floats_arr = ctypes.c_float * 3
    c_v0 = three_floats_arr(tri_1[0][0], tri_1[0][1], tri_1[0][2])
    c_v1 = three_floats_arr(tri_1[1][0], tri_1[1][1], tri_1[1][2])
    c_v2 = three_floats_arr(tri_1[2][0], tri_1[2][1], tri_1[2][2])

    c_u0 = three_floats_arr(tri_2[0][0], tri_2[0][1], tri_2[0][2])
    c_u1 = three_floats_arr(tri_2[1][0], tri_2[1][1], tri_2[1][2])
    c_u2 = three_floats_arr(tri_2[2][0], tri_2[2][1], tri_2[2][2])
    collision = C_MOLLERS.NoDivTriTriIsect(c_v0, c_v1, c_v2, c_u0, c_u1, c_u2)
    return collision


def devillers_alg(tri_1, tri_2):
    """
    Wrapper for the devillers algorithm that is implemented in C.

    Args:
        tri_1(list): A list of 3 lists with space coordinates in 3D space.
        tri_2(list): A list of 3 lists with space coordinates in 3D space.

    Returns:
        True if two triangles collide.
    """
    global C_DEVILLERS
    # int tri_tri_overlap_test_3d(p1,q1,r1,p2,q2,r2)
    three_doubles_arr = ctypes.c_double * 3
    c_p1 = three_doubles_arr(tri_1[0][0], tri_1[0][1], tri_1[0][2])
    c_q1 = three_doubles_arr(tri_1[1][0], tri_1[1][1], tri_1[1][2])
    c_r1 = three_doubles_arr(tri_1[2][0], tri_1[2][1], tri_1[2][2])

    c_p2 = three_doubles_arr(tri_2[0][0], tri_2[0][1], tri_2[0][2])
    c_q2 = three_doubles_arr(tri_2[1][0], tri_2[1][1], tri_2[1][2])
    c_r2 = three_doubles_arr(tri_2[2][0], tri_2[2][1], tri_2[2][2])
    collision = C_DEVILLERS.tri_tri_overlap_test_3d(c_p1, c_q1, c_r1, c_p2,
                                                    c_q2, c_r2)
    return collision