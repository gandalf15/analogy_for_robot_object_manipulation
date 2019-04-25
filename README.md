# Analogy
System for research of analogy in robot object manipulation.
For simplification, it is using axis-aligned bounding boxes.

- Design a scene in [Microsoft 3D builder](https://www.microsoft.com/en-gb/p/3d-builder/9wzdncrfj3t6?activetab=pivot:overviewtab)
- Teach the system what are the ideal manipulation points and force vectors for specific tasks.
- Use the knowledge to solve the manipulation tasks in unseen situations using an analogy.

## How to install

Required OS is either Ubuntu 16.04 (or later) or Fedora 29 (or later). Tested on both.

```bash
$ git clone git@github.com:gandalf15/analogy.git
$ cd analogy
$ make
$ chmod +x analogy.py
```

## How to use the system
Assuming the installation is done. As a first thing activate venv.

```bash
$ source venv/bin/activate
```
Then you can run the system. There are two options. The first option is to add new knowledge to the knowledge base database.
The second option is to solve or ask the system what are the best manipulation points and force vectors for a target object based on the current knowledge.
You can have multiple different databases with different knowledge.

### How to add new knowledge

This is a more general example of how to use the command.
```bash
./analogy.py add scene_name.obj knowledge_base.db
```

This is a specific example that will work immediately.
```bash
./analogy.py add scenes/books-shelf.obj knowledge_base.db
```

If a file with the name of the knowledge base database does not exist, it will be created.
If it exists, the knowledge will be added to the existing database.

You will see this scene.
![books-shelf scene](https://github.com/gandalf15/analogy/blob/master/images/books-shelf.png)

After the scene is opened and visualised in your web browser, select the target object for manipulation (click on it).

- Rotate the camera view: drag with the right mouse button (or Ctrl-drag left button).
- Zoom: drag with left and right mouse buttons (or Alt/Option-drag or scroll wheel).
- Pan: Shift-drag.
- Touch screen: swipe or two-finger rotate; pinch/extend to zoom.

This is how the target object changes opacity once it is selected.
![books-shelf scene](https://github.com/gandalf15/analogy/blob/master/images/books-shelf-2.png)

Then follow the instructions in the terminal window.
You will be asked to add the ideal manipulation points and force vectors for specific tasks.
Currently, it supports only 3 tasks. The manipulation tasks are push, pull and using a spatula.
In the end, knowledge is saved to the database.

The repository contains a few example scenes that you can find in `scenes` directory.

### How to use the knowledge

This is a more general example of how to use the command.
```bash
./analogy.py solve scene_name.obj knowledge_base.db
```

This is a specific example that will work immediately.
```bash
./analogy.py solve scenes/books-shelf.obj all_scenes.db
```

After the scene is opened and visualised in your web browser, select the target object for manipulation (click on it).

- Rotate the camera view: drag with the right mouse button (or Ctrl-drag left button).
- Zoom: drag with left and right mouse buttons (or Alt/Option-drag or scroll wheel).
- Pan: Shift-drag.
- Touch screen: swipe or two-finger rotate; pinch/extend to zoom.

For example the middle book on the shelf. Then confirm the selection in the terminal window.
You should now see the suggested manipulation points and their force vectors for specific tasks.

![books-shelf scene](https://github.com/gandalf15/analogy/blob/master/images/books-shelf-3.png)

White spheres are colliders for each axis-aligned bounding box.

Cyan color = push \
Purple color = pull \
Orange color = using spatula \

### Interesting stuff

It is interesting to see how the analogy works with limited knowledge.
For example, `books-shelf.db` contains only knowledge about how to manipulate the middle book in scene `scenes/books-shelf.obj`.
Now, if I want to solve a manipulation problem for a pizza box in a freezer in the scene `scenes/pizza-boxes-freezer.obj`, I just have to run this command.

```bash
./analogy.py solve scenes/pizza-boxes-freezer.obj books-shelf.db
```

Notice that the last argument is the knowledge base we want to use.

You will see this scene.
![pizza-freezer scene](https://github.com/gandalf15/analogy/blob/master/images/pizza-freezer.png)

Now you have to rotate the scene so you can select the target object (pizza box in the middle).
![pizza-freezer scene](https://github.com/gandalf15/analogy/blob/master/images/pizza-freezer-2.png)

After you confirm the selection in the terminal window you can see this suggested points and force vectors.
![pizza-freezer scene](https://github.com/gandalf15/analogy/blob/master/images/pizza-freezer-3.png)
