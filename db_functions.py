import psycopg2 as pg

def create_db(cursor):

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

def delete_table(cursor):

    cursor.execute('''
        DROP TABLE IF EXISTS person_info;
        DROP TABLE IF EXISTS person_viewed;
        ''')

def add_user_info_to_db(cursor, user: dict):

    cursor.execute('''
            INSERT INTO person_info(vk_id, first_name, last_name,
            candidate_info_rating)
            VALUES(%s, %s, %s, %s);
            ''', (
                  user.get('vk_id'), user.get('first_name'),
                  user.get('last_name'), (user.get('candidate_info_rating'),
                  )))

def add_user_coefficients(cursor, user: dict):

    cursor.execute('''
        INSERT INTO person_info(candidate_info_coefficient, mutual_groups_coefficient)
        VALUES(%s, %s);
        ''', (user.get('candidate_info_coefficient'), user.get('mutual_groups_coefficient')))

def add_to_viewed(cursor, user_id):

    cursor.execute('''
            INSERT INTO person_viewed(vk_id)
            VALUES(%s);
            ''', (user_id,))

def delete_from_db(cursor, user_id):

    cursor.execute('''
        DELETE FROM person_info
        WHERE vk_id = (%s);
        ''', (user_id,))

def get_users(cursor):

    cursor.execute('''
        SELECT * FROM person_info
        ORDER BY candidate_info_rating DESC;
        ''')
    return cursor.fetchall()

def get_users_black_list(cursor):

    cursor.execute('''
        SELECT * FROM person_viewed;
                      ''')
    return cursor.fetchall()
