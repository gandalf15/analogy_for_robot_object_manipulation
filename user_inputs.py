import statistics as stat
import analogy.vpython_drawings as vpython_drawings


def select_object(vpython_scene):
    picked_vpython_obj = None

    def pick_obj():
        nonlocal picked_vpython_obj
        picked_vpython_obj = vpython_scene.mouse.pick
        vpython_scene.unbind('mousedown', pick_obj)

    while picked_vpython_obj is None:
        vpython_scene.bind('mousedown', pick_obj)
        vpython_scene.title = 'To select the target object, please click on it.'
        vpython_scene.waitfor('mousedown')
        if picked_vpython_obj is not None:
            picked_vpython_obj.opacity = 0.8
            user_input = input(
                'Now you should see the the selected object as highlighted. Is that a correct object? yes/no: '
            )
            if user_input.lower() != 'yes' and user_input.lower() != 'y':
                print('OK try again!')
                picked_vpython_obj.opacity = 0.4
                user_input = None
                picked_vpython_obj = None
                vpython_scene.bind('mousedown', pick_obj)
    picked_vpython_obj.opacity = 0.8
    vpython_scene.center = picked_vpython_obj.pos
    return picked_vpython_obj


def get_point(vpython_scene, picked_obj, picked_vpython_obj, operation):
    vpython_scene.title = 'Follow instructions in the terminal window.'
    user_message = ['\nSelect manipulation point for ' + operation + '.']
    user_message.append('It has to be in form of "X, Y, Z"')
    user_message.append('Notice that the coordinates are separated by comma.')
    user_message.append('the object has half size: ' +
                        str(picked_obj.aabb.half_size))
    user_message.append('and XYZ coordinates of the middle point: : ' +
                        str(picked_obj.aabb.pos))
    user_message.append(operation + ' manipulation point X,Y,Z or none: ')
    user_input = None
    while user_input == None:
        user_input = input("\n".join(user_message))
        point_list = user_input.split(',')
        if len(point_list) == 3:
            picked_obj.aabb.manipulation_points[operation] = [
                float(point_list[0].strip()),
                float(point_list[1].strip()),
                float(point_list[2].strip())
            ]
            radius = stat.mean(picked_obj.aabb.half_size) / 10
            vpython_point = vpython_drawings.draw_point(
                picked_obj.aabb.manipulation_points[operation], radius)
            picked_vpython_obj.opacity = 0.4
            user_input = input(
                'Now you should see the point. Is that correct location? yes/no: '
            )
            if user_input.lower() != 'yes' and user_input.lower() != 'y':
                print('OK try again!')
                vpython_point.visible = False
                del vpython_point
                user_input = None
        elif user_input.lower() == 'none':
            picked_obj.aabb.manipulation_points[operation] = [None, None, None]
        else:
            user_input = None
            print('\nWrong input. Try again!')


def get_vector(vpython_scene, picked_obj, picked_vpython_obj, operation):
    if picked_obj.aabb.manipulation_points[operation][0] is not None:
        # get force vector for pushing
        user_message = ['\nSelect force vector for ' + operation + '.']
        user_message.append('It has to be in form of "X, Y, Z"')
        user_message.append(operation + ' force vector X,Y,Z: ')
        user_input = None
        while user_input == None:
            user_input = input("\n".join(user_message))
            force_vec = user_input.split(',')
            if len(force_vec) == 3:
                picked_obj.aabb.manipulation_vectors[operation] = [
                    float(force_vec[0].strip()),
                    float(force_vec[1].strip()),
                    float(force_vec[2].strip())
                ]
                length = stat.mean(picked_obj.aabb.half_size)
                vpython_arrow = vpython_drawings.draw_arrow(
                    picked_obj.aabb.manipulation_points[operation],
                    picked_obj.aabb.manipulation_vectors[operation], length)
                user_input = input(
                    'Now you should see the force arrow. Is that correct ? yes/no: '
                )
                if user_input.lower() != 'yes' and user_input.lower() != 'y':
                    print('OK try again!')
                    vpython_arrow.visible = False
                    del vpython_arrow
                    user_input = None
            else:
                user_input = None
                print('Wrong input. Try again!')
    else:
        picked_obj.aabb.manipulation_vectors[operation] = [None, None, None]
