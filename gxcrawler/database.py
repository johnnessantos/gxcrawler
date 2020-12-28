'''database manager'''
import os
import sqlite3


class DataBase():
    '''
    Class database operations
    '''
    def __init__(self, database_path=None):
        self.in_memory = None
        self.conn = None

        if database_path:
            self.__database_path = database_path
        else:
            self.__database_path = os.getcwd()+os.path.sep+'database.db'

        self.conn = self.__generate_db(self.__database_path, False)

    def get_database_path(self):
        '''
        Method get path of file db sqlite
        '''
        return self.__database_path

    def __generate_db(self, path=None, in_memory=False):
        '''
        Generate db
        '''
        self.in_memory = in_memory
        if in_memory:
            conn = sqlite3.connect(':memory:')
            return conn
        else:
            if not os.path.isfile(path):
                print('Creating database...')

            conn = sqlite3.connect(path)
            return conn

    def construct_schema(self):
        '''
        Construct schema in database
        '''
        schema = '''
            CREATE TABLE IF NOT EXISTS revision(
                revision_build INTEGER PRIMARY KEY,
                revision_date TEXT,
                revision_seconds INTEGER,
                revision_user TEXT,
                revision_comment TEXT,
                revision_name TEXT,
                revision_operation TEXT
            );

            CREATE TABLE IF NOT EXISTS revision_objects(
                revision_build INTEGER,
                object_type TEXT,
                object_name TEXT,
                object_gu_id TEXT,
                object_entity_id INTEGER,
                object_operation TEXT,
                FOREIGN KEY(revision_build) REFERENCES revision(revision_build)
            );
        '''

        cursor = self.conn.cursor()
        cursor.executescript(schema)
        self.conn.commit()
        cursor.close()

    def insert_revision(self, rev):
        '''
        Insert revision and revision_objects in database
        Params:
        ------
            rev: List<Dict>
        Returns:
        ------
            None
        '''
        try:
            cursor = self.conn.cursor()
            cursor.executemany('''
                INSERT INTO revision(
                    revision_build, revision_date, revision_seconds,
                    revision_user, revision_comment,
                    revision_name, revision_operation)
                VALUES(?, ?, ?, ?, ?, ?, ?)''', [(
                    int(rev["revision_build"]), rev["revision_date"],
                    int(rev["revision_seconds"]),
                    rev["revision_user"], rev["revision_comment"],
                    rev["revision_name"],
                    rev["revision_operation"])
                ]
            )

            # Inserting objects of revision
            revision_objects = []
            for rev_obj in rev["revision_objects"]:
                revision_objects.append(
                    (
                        int(rev["revision_build"]), rev_obj["object_type"],
                        rev_obj["object_name"],
                        rev_obj["object_gu_id"],
                        int(rev_obj["object_entity_id"]),
                        rev_obj["object_operation"]
                    )
                )

            cursor.executemany('''
                    INSERT INTO revision_objects(
                        revision_build, object_type, object_name,
                        object_gu_id, object_entity_id,
                        object_operation)
                    VALUES(?, ?, ?, ?, ?, ?)''', revision_objects)

            self.conn.commit()
            cursor.close()
        except sqlite3.IntegrityError as integrity_error:
            print(rev)
            raise sqlite3.IntegrityError() from integrity_error


if __name__ == '__main__':
    database = DataBase()
    print(f'database path: {database.get_database_path()}')
    database.construct_schema()
