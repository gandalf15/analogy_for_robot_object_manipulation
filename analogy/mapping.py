import heapq
import operator

import vpython

from analogy.mesh import AABB


class Mapping:
    """
    Class Mapping holds all necessary methods for analogy mapping.
    
    Attributes:
        mapping_sides(dict): Dict literal that represents how surfaces are
            rotated along X and Y axis. This is late used in creating all
            permutations.
        permutations_tuple(tuple): Permutation sequences for a cube.
        all_permutations(dict): Dict of all permutation sequences where key is
            the sequence and vlue is dict of surface mappings.
    """

    def __init__(self):
        """Init Mapping with all permutations of cuboid surfaces."""
        # clockwise rotation
        self.mapping_sides = {
            'x': ['top', 'back', 'bottom', 'front'],
            'y': ['front', 'left', 'back', 'right']
        }

        # yapf: disable
        self.permutations_tuple = (('i'), ('x'), ('y'), ('x', 'x'), ('x', 'y'), ('y', 'x'),
                            ('y', 'y'), ('x', 'x', 'x'), ('x', 'x', 'y'),
                            ('x', 'y', 'x'), ('x', 'y', 'y'), ('y', 'x', 'x'),
                            ('y', 'y', 'x'), ('y', 'y', 'y'), ('x', 'x', 'x', 'y'),
                            ('x', 'x', 'y', 'x'), ('x', 'x', 'y', 'y'),
                            ('x', 'y', 'x', 'x'), ('x', 'y', 'y', 'y'),
                            ('y', 'x', 'x', 'x'), ('y', 'y', 'y', 'x'),
                            ('x', 'x', 'x', 'y', 'x'), ('x', 'y', 'x', 'x', 'x'),
                            ('x', 'y', 'y', 'y', 'x'))
        # yapf: enable
        self.all_permutations = self.create_permutations()

    def create_permutations(self):
        """
        It creates all permutations of cuboid surfaces

        Returns:
            Dict of all permutation sequences where key is
            the sequence and vlue is dict of surface mappings.
            For example:
            {
                ('i'): {'top': 'top', 'bottom': 'bottom', 'front': 'front',
                'back': 'back', 'right': 'right', 'left': 'left',}
                ('x'):{'top': 'back', 'bottom': 'front', 'front': 'top', 
                'back': 'bottom', 'right': 'right', 'left': 'left',}
                ...
            }
        """
        permutations = {}
        for permutation in self.permutations_tuple:
            sides = {
                'top': 'top',
                'bottom': 'bottom',
                'front': 'front',
                'back': 'back',
                'right': 'right',
                'left': 'left',
            }
            for step in reversed(permutation):
                if step == 'i':
                    break
                for key in sides.keys():
                    if sides[key] in self.mapping_sides[step]:
                        side_index = self.mapping_sides[step].index(sides[key])
                        next_index = (side_index + 1) % len(
                            self.mapping_sides[step])
                        sides[key] = self.mapping_sides[step][next_index]
            permutations[permutation] = sides
        return permutations

    def get_mappings_score(self, target_aabb, source_aabb):
        """
        Returns analogy scores for all mappings of two AABB objects.

        Args:
            target_aabb(AABB): The target AABB that we want to map to source AABB.
            source_aabb(AABB): The source AABB that from source scene.

        Returns:
            Analogy scores for all mappings (sequence permutations) of two AABB 
            objects based on collided sides simmilarity, ratio of AABBs, 
            matching surfaces.
        """
        # collision match weights
        exact_collision_weight = 0.99  #0.9
        partial_collision_weight = 0.5  #0.4
        no_collision_match_weight = .0  #-0.1
        # surface match weights
        top_match_weight = .02  #0.1
        bottom_match_weight = .02  #0.1
        front_match_weight = .01  #0.01
        back_match_weight = .01  #0.01
        right_match_weight = .01  #0.01
        left_match_weight = .01  #0.01
        no_surf_match_weight = .0  #-0.01
        # surface ratio difference penalties
        xy_ratio_weight = 0.1
        zy_ratio_weight = 0.1
        xz_ratio_weight = 0.1

        mappings_score = []
        for perm_sequence in self.all_permutations.keys():
            score = 1.0  # default score
            for surface in self.all_permutations[perm_sequence].keys():
                # scores for exact collision/partial/no-collision match
                if target_aabb.collided_sides[
                        surface] == source_aabb.collided_sides[
                            self.all_permutations[perm_sequence][surface]]:
                    score += 1.0 * exact_collision_weight
                # match partially collided sides and fully collided sides
                elif target_aabb.collided_sides[
                        surface] != 0 and source_aabb.collided_sides[
                            self.all_permutations[perm_sequence][surface]] != 0:
                    score += 1.0 * partial_collision_weight
                else:  # there is no match
                    score += 1.0 * no_collision_match_weight

                # score for surface match
                if (surface == 'top' and
                        self.all_permutations[perm_sequence][surface] == 'top'):
                    score += 1.0 * top_match_weight
                elif (surface == 'bottom' and
                      self.all_permutations[perm_sequence][surface] == 'bottom'
                     ):
                    score += 1.0 * bottom_match_weight
                elif (surface == 'front' and
                      self.all_permutations[perm_sequence][surface] == 'front'):
                    score += 1.0 * front_match_weight
                elif (surface == 'back' and
                      self.all_permutations[perm_sequence][surface] == 'back'):
                    score += 1.0 * back_match_weight
                elif (surface == 'right' and
                      self.all_permutations[perm_sequence][surface] == 'right'):
                    score += 1.0 * right_match_weight
                elif (surface == 'left' and
                      self.all_permutations[perm_sequence][surface] == 'left'):
                    score += 1.0 * left_match_weight
                else:
                    score += 1.0 * no_surf_match_weight
            # create vpython vec for xyz half size of the target object
            vpython_vec_xyz = vpython.vec(target_aabb.half_size[0],
                                          target_aabb.half_size[1],
                                          target_aabb.half_size[2])
            # rotate it based on rotation sequence
            for rotation in reversed(perm_sequence):
                if rotation == 'x':
                    vpython_vec_xyz = vpython.rotate(
                        vpython_vec_xyz,
                        angle=vpython.radians(-90),
                        axis=vpython.vec(1, 0, 0))
                elif rotation == 'y':
                    vpython_vec_xyz = vpython.rotate(
                        vpython_vec_xyz,
                        angle=vpython.radians(-90),
                        axis=vpython.vec(0, 1, 0))
            # compare xy, zy, xz ratios of target and source aabbs after rotation
            # and penalise for difference
            xy_ratio_diff = abs(
                (abs(vpython_vec_xyz.x) / abs(vpython_vec_xyz.y)) -
                (source_aabb.half_size[0] / source_aabb.half_size[1]))
            xy_ratio_diff *= xy_ratio_weight
            zy_ratio_diff = abs(
                (abs(vpython_vec_xyz.z) / abs(vpython_vec_xyz.y)) -
                (source_aabb.half_size[2] / source_aabb.half_size[1]))
            zy_ratio_diff *= zy_ratio_weight
            xz_ratio_diff = abs(
                (abs(vpython_vec_xyz.x) / abs(vpython_vec_xyz.z)) -
                (source_aabb.half_size[0] / source_aabb.half_size[2]))
            xz_ratio_diff *= xz_ratio_weight
            sum_ratio_diff = xy_ratio_diff + zy_ratio_diff + xz_ratio_diff

            # penalise for ratio difference
            score -= sum_ratio_diff

            mappings_score.append((score, perm_sequence))
        return mappings_score


if __name__ == '__main__':
    # For testing purposes
    target_obj_1 = AABB([0, 0, 0], [10, 10, 10])
    collided_sides_1 = {
        'top': 2,
        'bottom': 2,
        'front': 0,
        'back': 2,
        'right': 2,
        'left': 0,
    }
    target_obj_1.collided_sides = collided_sides_1
    source_obj_2 = AABB([50, 0, 0], [20, 10, 30])
    collided_sides_2 = {
        'top': 0,
        'bottom': 2,
        'front': 0,
        'back': 2,
        'right': 2,
        'left': 2,
    }
    source_obj_2.collided_sides = collided_sides_2
    mapping = Mapping()
    mappings_score = mapping.get_mappings_score(
        target_aabb=target_obj_1, source_aabb=source_obj_2)
    print()
    print('-' * 120)
    for score_perm in heapq.nlargest(
            5, mappings_score, key=operator.itemgetter(0)):
        print(mapping.all_permutations[score_perm[1]])
        print('permutation:', score_perm[1], 'Score:', score_perm[0])
        print('-' * 120)
