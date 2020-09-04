import psycopg2 as pg
from db_config import db_config


class DB_functions:

    def __init__(self):
        self.conn = pg.connect(
                  database=db_config['database'],
                  user=db_config['user'],
                  password=db_config['password'],
                  host=db_config['host'],
                  port=db_config['port']
                 )
        
    def create_db(self):

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS person_info
                (user_id SERIAL PRIMARY KEY NOT NULL,
                vk_id INTEGER NOT NULL,
                first_name VARCHAR(30) NOT NULL,
                last_name VARCHAR(40) NOT NULL,
                candidate_info_rating INT NULL);

                CREATE TABLE IF NOT EXISTS person_viewed
                (user_id SERIAL NOT NULL,
                vk_id INTEGER PRIMARY KEY NOT NULL);
                '''
            )

    def delete_table(self):

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                DROP TABLE IF EXISTS person_info;
                DROP TABLE IF EXISTS person_viewed;
                ''')

    def add_user_info_to_db(self, user: dict):

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                    INSERT INTO person_info(vk_id, first_name, last_name,
                    candidate_info_rating)
                    VALUES(%s, %s, %s, %s);
                    ''', (
                user.get('vk_id'), user.get('first_name'),
                user.get('last_name'), (user.get('candidate_info_rating'),
                                        )))

    def add_user_coefficients(self, user: dict):

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO person_info(candidate_info_coefficient, mutual_groups_coefficient)
                VALUES(%s, %s);
                ''', (user.get('candidate_info_coefficient'), user.get('mutual_groups_coefficient')))

    def add_to_viewed(self, user_id):

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                    INSERT INTO person_viewed(vk_id)
                    VALUES(%s);
                    ''', (user_id,))

    def delete_from_db(self, user_id):

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                DELETE FROM person_info
                WHERE vk_id = (%s);
                ''', (user_id,))

    def get_users(self, cursor):

        cursor.execute('''
            SELECT * FROM person_info
            ORDER BY candidate_info_rating DESC;
            ''')
        return cursor.fetchall()

    def get_users_black_list(self):

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM person_viewed;
                              ''')
            return cursor.fetchall()

    def get_top10_users(self):

        print('Выводим данные 10 наиболее перспективных кандидатов:')
    # Вытаскиваем из бд данные топ-10 юзеров.
        with self.conn:
            cursor = self.conn.cursor()
            list_of_ten = self.get_users(cursor)[0:10]
            return list_of_ten
