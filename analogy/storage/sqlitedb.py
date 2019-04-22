import sqlite3
import os
import pickle


class sqlitedb:
    """
    sqlitedb represents the sqlite database and provides methods for 
    analogy system. 

    Attributes:
        name(str): name for the database file. Default ':memory:'.
        conn(sqlite3.Connection): It represents the database.
        cursor(sqlite3.Cursor): It represents the cursor for the database.
    """

    def __init__(self, name=':memory:'):
        """
        Inits sqlitedb.

        Args:
            name(str): Optional. Name for the database file. Default ':memory:'.
        """
        self.name = name
        self.conn = sqlite3.connect(self.name)
        self.cursor = self.conn.cursor()

    def drop_db(self):
        """Drops the whole database"""
        os.remove(self.name)

    def create_db(self):
        """Creates the whole database for analogy system"""
        # Create TargetAABB table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS TargetAABB (
            ID INTEGER PRIMARY KEY,
            FileName TEXT NOT NULL,
            PositionID INTEGER,
            PushPointID INTEGER,
            PushVectorID INTEGER,
            PullPointID INTEGER,
            PullVectorID INTEGER,
            SpatulaPointID INTEGER,
            SpatulaVectorID INTEGER ,
            HalfSizeX REAL NOT NULL,
            HalfSizeY REAL NOT NULL,
            HalfSizeZ REAL NOT NULL,
            CollidedTop INTEGER DEFAULT 0,
            CollidedBottom INTEGER DEFAULT 0,
            CollidedFront INTEGER DEFAULT 0,
            CollidedBack INTEGER DEFAULT 0,
            CollidedRight INTEGER DEFAULT 0,
            CollidedLeft INTEGER DEFAULT 0,
            FOREIGN KEY (PositionID) REFERENCES Position (ID),
            FOREIGN KEY (PushPointID) REFERENCES PushPoint (ID),
            FOREIGN KEY (PushVectorID) REFERENCES PushVector (ID),
            FOREIGN KEY (PullPointID) REFERENCES PullPoint (ID),
            FOREIGN KEY (PullVectorID) REFERENCES PullVector (ID),
            FOREIGN KEY (SpatulaPointID) REFERENCES SpatulaPoint (ID),
            FOREIGN KEY (SpatulaVectorID) REFERENCES SpatulaVector (ID)
        )''')

        # Create Position table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Position (
            ID INTEGER PRIMARY KEY,
            X REAL,
            Y REAL,
            Z REAL
        )''')

        # Create PushPoint table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS PushPoint (
            ID INTEGER PRIMARY KEY,
            PositionID INTEGER,
            FOREIGN KEY (PositionID) REFERENCES Position (ID)
        )''')

        # Create PushVector table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS PushVector (
            ID INTEGER PRIMARY KEY,
            VectorX INTEGER,
            VectorY INTEGER,
            VectorZ INTEGER
        )''')

        # Create PullPoint table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS PullPoint (
            ID INTEGER PRIMARY KEY,
            PositionID INTEGER,
            FOREIGN KEY (PositionID) REFERENCES Position (ID)
        )''')

        # Create PullVector table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS PullVector (
            ID INTEGER PRIMARY KEY,
            VectorX INTEGER,
            VectorY INTEGER,
            VectorZ INTEGER
        )''')

        # Create SpatulaPoint table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS SpatulaPoint (
            ID INTEGER PRIMARY KEY,
            PositionID INTEGER,
            FOREIGN KEY (PositionID) REFERENCES Position (ID)
        )''')

        # Create SpatulaVector table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS SpatulaVector (
            ID INTEGER PRIMARY KEY,
            VectorX INTEGER,
            VectorY INTEGER,
            VectorZ INTEGER
        )''')

        self.conn.commit()

    def _select_pos(self, pos):
        self.cursor.execute(
            '''SELECT ID FROM Position WHERE X=? AND Y=? AND Z=?''', pos)
        return self.cursor.fetchone()

    def _insert_pos(self, pos):
        self.cursor.execute('''INSERT INTO Position(X, Y, Z) VALUES(?,?,?)''',
                            pos)
        return self.cursor.lastrowid

    def save_scene(self, scene, scene_name, target_object):
        """
        Saves the scene information to the database.

        Args:
            scene(dict): A dict of Mest objects where the key is the name of 
                the mesh and value is Mesh object.
            scene_name(str): The name of the scene.
            target_object(Mesh): The target object in the scene.

        Returns:
            ID of the new (may be existing entry) entry in TargetAABB table.
        """
        # save scene to the file
        file_path = './scenes/pkl/' + scene_name + '.pkl'
        with open(file_path, 'wb') as f:
            pickle.dump(scene, f, pickle.HIGHEST_PROTOCOL)
        # save additional data to database
        # Save Position
        aabb_pos_id = self._select_pos(target_object.aabb.pos)
        if aabb_pos_id is None:
            aabb_pos_id = self._insert_pos(target_object.aabb.pos)
        else:
            aabb_pos_id = aabb_pos_id[0]

        # Save PushPoint
        push_pos_id = self._select_pos(
            target_object.aabb.manipulation_points['push'])
        if push_pos_id is None:
            push_pos_id = self._insert_pos(
                target_object.aabb.manipulation_points['push'])
        else:
            push_pos_id = push_pos_id[0]

        self.cursor.execute('''SELECT ID FROM PushPoint WHERE PositionID=?''',
                            (push_pos_id,))
        push_point_id = self.cursor.fetchone()
        if push_point_id is None:
            self.cursor.execute(
                '''INSERT INTO PushPoint(PositionID) VALUES(?)''',
                (push_pos_id,))
            push_point_id = self.cursor.lastrowid
        else:
            push_point_id = push_point_id[0]

        # Save PushVector
        self.cursor.execute(
            '''SELECT ID FROM PushVector WHERE VectorX=? AND VectorY=? AND VectorZ=?''',
            target_object.aabb.manipulation_vectors['push'])
        push_vec_id = self.cursor.fetchone()
        if push_vec_id is None:
            self.cursor.execute(
                '''INSERT INTO PushVector(VectorX, VectorY, VectorZ) VALUES(?,?,?)''',
                target_object.aabb.manipulation_vectors['push'])
            push_vec_id = self.cursor.lastrowid
        else:
            push_vec_id = push_vec_id[0]

        # Save PullPoint
        pull_pos_id = self._select_pos(
            target_object.aabb.manipulation_points['pull'])
        if pull_pos_id is None:
            pull_pos_id = self._insert_pos(
                target_object.aabb.manipulation_points['pull'])
        else:
            pull_pos_id = pull_pos_id[0]

        self.cursor.execute('''SELECT ID FROM PullPoint WHERE PositionID=?''',
                            (pull_pos_id,))
        pull_point_id = self.cursor.fetchone()
        if pull_point_id is None:
            self.cursor.execute(
                '''INSERT INTO PullPoint(PositionID) VALUES(?)''',
                (pull_pos_id,))
            pull_point_id = self.cursor.lastrowid
        else:
            pull_point_id = pull_point_id[0]

        # Save PullVector
        self.cursor.execute(
            '''SELECT ID FROM PullVector WHERE VectorX=? AND VectorY=? AND VectorZ=?''',
            target_object.aabb.manipulation_vectors['pull'])
        pull_vec_id = self.cursor.fetchone()
        if pull_vec_id is None:
            self.cursor.execute(
                '''INSERT INTO PullVector(VectorX, VectorY, VectorZ) VALUES(?,?,?)''',
                target_object.aabb.manipulation_vectors['pull'])
            pull_vec_id = self.cursor.lastrowid
        else:
            pull_vec_id = pull_vec_id[0]

        # Save SpatulaPoint
        spatula_pos_id = self._select_pos(
            target_object.aabb.manipulation_points['spatula'])
        if spatula_pos_id is None:
            spatula_pos_id = self._insert_pos(
                target_object.aabb.manipulation_points['spatula'])
        else:
            spatula_pos_id = spatula_pos_id[0]

        self.cursor.execute(
            '''SELECT ID FROM SpatulaPoint WHERE PositionID=?''',
            (spatula_pos_id,))
        spatula_point_id = self.cursor.fetchone()
        if spatula_point_id is None:
            self.cursor.execute(
                '''INSERT INTO SpatulaPoint(PositionID) VALUES(?)''',
                (spatula_pos_id,))
            spatula_point_id = self.cursor.lastrowid
        else:
            spatula_point_id = spatula_point_id[0]

        # Save SpatulaVector
        self.cursor.execute(
            '''SELECT ID FROM SpatulaVector WHERE VectorX=? AND VectorY=? AND VectorZ=?''',
            target_object.aabb.manipulation_vectors['spatula'])
        spatula_vec_id = self.cursor.fetchone()
        if spatula_vec_id is None:
            self.cursor.execute(
                '''INSERT INTO SpatulaVector(VectorX, VectorY, VectorZ) VALUES(?,?,?)''',
                target_object.aabb.manipulation_vectors['spatula'])
            spatula_vec_id = self.cursor.lastrowid
        else:
            spatula_vec_id = spatula_vec_id[0]

        # Save TargetAABB
        self.cursor.execute(
            '''SELECT ID FROM TargetAABB WHERE FileName=? AND PositionID=? AND
            PushPointID=? AND PushVectorID=? AND PullPointID=? AND PullVectorID=? AND
            SpatulaPointID=? AND SpatulaVectorID=? AND HalfSizeX=? AND HalfSizeY=? AND
            HalfSizeZ=? AND CollidedTop=? AND CollidedBottom=? AND CollidedFront=? AND
            CollidedBack=? AND CollidedRight=? AND CollidedLeft=?''',
            (file_path, aabb_pos_id, push_point_id, push_vec_id, pull_point_id,
             pull_vec_id, spatula_point_id, spatula_vec_id,
             target_object.aabb.half_size[0], target_object.aabb.half_size[1],
             target_object.aabb.half_size[2],
             target_object.aabb.collided_sides['top'],
             target_object.aabb.collided_sides['bottom'],
             target_object.aabb.collided_sides['front'],
             target_object.aabb.collided_sides['back'],
             target_object.aabb.collided_sides['right'],
             target_object.aabb.collided_sides['left']))
        target_aabb_id = self.cursor.fetchone()
        if target_aabb_id is None:
            self.cursor.execute(
                '''INSERT INTO TargetAABB(
            FileName, PositionID, PushPointID, PushVectorID, PullPointID,
            PullVectorID, SpatulaPointID, SpatulaVectorID, HalfSizeX, HalfSizeY,
            HalfSizeZ, CollidedTop, CollidedBottom, CollidedFront, CollidedBack,
            CollidedRight, CollidedLeft
            )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (file_path, aabb_pos_id, push_point_id, push_vec_id,
                 pull_point_id, pull_vec_id, spatula_point_id, spatula_vec_id,
                 target_object.aabb.half_size[0],
                 target_object.aabb.half_size[1],
                 target_object.aabb.half_size[2],
                 target_object.aabb.collided_sides['top'],
                 target_object.aabb.collided_sides['bottom'],
                 target_object.aabb.collided_sides['front'],
                 target_object.aabb.collided_sides['back'],
                 target_object.aabb.collided_sides['right'],
                 target_object.aabb.collided_sides['left']))

        self.conn.commit()
        return target_aabb_id

    def select_all_aabbs(self):
        self.cursor.execute('''SELECT * FROM TargetAABB''')
        results = self.cursor.fetchall()
        return results

    def select_aabb_id(self, id):
        self.cursor.execute('''SELECT * FROM TargetAABB WHERE ID=?''', (id,))
        result = self.cursor.fetchone()
        return result

    def select_all_positions(self):
        self.cursor.execute('''SELECT * FROM Position''')
        results = self.cursor.fetchall()
        return results

    def select_position_id(self, id):
        self.cursor.execute('''SELECT * FROM Position WHERE ID=?''', (id,))
        result = self.cursor.fetchone()
        return result

    def select_all_push_points(self):
        self.cursor.execute('''SELECT * FROM PushPoint''')
        results = self.cursor.fetchall()
        return results

    def select_push_point_id(self, id):
        self.cursor.execute('''SELECT * FROM PushPoint WHERE ID=?''', (id,))
        result = self.cursor.fetchone()
        return result

    def select_all_push_vec(self):
        self.cursor.execute('''SELECT * FROM PushVector''')
        results = self.cursor.fetchall()
        return results

    def select_push_vec_id(self, id):
        self.cursor.execute('''SELECT * FROM PushVector WHERE ID=?''', (id,))
        result = self.cursor.fetchone()
        return result

    def select_all_pull_points(self):
        self.cursor.execute('''SELECT * FROM PullPoint''')
        results = self.cursor.fetchall()
        return results

    def select_pull_point_id(self, id):
        self.cursor.execute('''SELECT * FROM PullPoint WHERE ID=?''', (id,))
        result = self.cursor.fetchone()
        return result

    def select_all_pull_vec(self):
        self.cursor.execute('''SELECT * FROM PullVector''')
        results = self.cursor.fetchall()
        return results

    def select_pull_vec_id(self, id):
        self.cursor.execute('''SELECT * FROM PullVector WHERE ID=?''', (id,))
        result = self.cursor.fetchone()
        return result

    def select_all_spatula_points(self):
        self.cursor.execute('''SELECT * FROM SpatulaPoint''')
        results = self.cursor.fetchall()
        return results

    def select_spatula_point_id(self, id):
        self.cursor.execute('''SELECT * FROM SpatulaPoint WHERE ID=?''', (id,))
        result = self.cursor.fetchone()
        return result

    def select_all_spatula_vec(self):
        self.cursor.execute('''SELECT * FROM SpatulaVector''')
        results = self.cursor.fetchall()
        return results

    def select_spatula_vec_id(self, id):
        self.cursor.execute('''SELECT * FROM SpatulaVector WHERE ID=?''', (id,))
        result = self.cursor.fetchone()
        return result


if __name__ == '__main__':
    # For testing purposes
    db = sqlitedb('kb.db')
    db.create_db()
    # db.drop_db()
    print(db.select_aabb_id(1))
    db.conn.close()
