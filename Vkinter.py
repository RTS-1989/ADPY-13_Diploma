import requests
import json
import datetime
import time
import db_functions
import psycopg2 as pg
from time import sleep

# Введите свой токен
token = ''
API = 'https://api.vk.com/method'

class Vkinter:

    def __init__(self, user_id: int, token):
        self.token = token
        self.user_id = user_id
        
    def get_user_info(self, user_id: int) -> dict:

        params = {
              'access_token': token,
              'user_ids': user_id,
              'v': 5.107,
              'fields': f'sex, bdate, city, country, domain, \
              relation, activities, interests, music, movies, \
              tv, books, games, about, is_favorite, is_friend, \
              common_count, can_see_audio, screen_name'
              }
    
        response = requests.get(f'{API}/users.get', params).json()['response'][0]

        return response

    def user_text_info_check(self, list_of_names):
        list_of_interests = []

        city = input('Введите город для поиска: ->')

        city_id = 0

        if city == 'Москва' or city == 'Санкт-Петербург':
            city_id += Vkinter.get_city_id(city)
        else:
            region = input('Укажите регион без слова "область, край или республика"\
для города, в котором выхотите вести поиск: ->')
            city_id += Vkinter.get_city_id(city, region)

        age_from = input('Введите начало диапазона возрастов ->')
        age_to = input('Введите конец диапазона возрастов ->')

        for name in list_of_names:
            candidates_info = self.search_for_users(self.user_id, age_from, age_to, city_id, name)
            for candidate in candidates_info:
                if 'music' in candidate.keys():
                    list_of_interests.append(
                                             {
                                             'id': candidate['id'],
                                             'first_name': candidate['first_name'],
                                             'last_name': candidate['last_name'],
                                             'music': candidate['music'],
                                             'interests': candidate['interests'],
                                             'movies': candidate['movies'],
                                             'books': candidate['movies']
                                             }
                                             )
        return list_of_interests

    def get_user_interests_coefficient(self, list_of_interests):
        print('Добавляем кандидатов в базу данных')
        interests_coefficient = 3
        music_coefficient = 10
        movies_coefficient = 5
        books_coefficient = 7
        user_info = self.get_user_info(self.user_id)   
        info = {}
        sums_of_coefficients = []
        
        user_interests_info = set(user_info['interests'].lower().split(', '))
        user_music_info = set(user_info['music'].lower().split(', '))
        user_movies_info = set(user_info['movies'].lower().split(', '))
        user_books_info = set(user_info['books'].lower().split(', '))
                               
        for candidate_info in list_of_interests:
            info[candidate_info['id']] = {}
            interests_intersection = user_interests_info.intersection(
                set(candidate_info['interests'].lower().split(', ')))
            music_intersection = user_music_info.intersection(
                set(candidate_info['music'].lower().split(', ')))
            movies_intersection = user_movies_info.intersection(
                set(candidate_info['movies'].lower().split(', ')))
            books_intersection = user_books_info.intersection(
                set(candidate_info['books'].lower().split(', ')))

            info[candidate_info['id']].update({'Общие_интересы': len(interests_intersection)})
            info[candidate_info['id']].update({'Общая_музыка': len(music_intersection)})
            info[candidate_info['id']].update({'Общие_фильмы': len(movies_intersection)})
            info[candidate_info['id']].update({'Общие_книги': len(books_intersection)})

        for candidate_interests_rating in info:
            interests_rating = info[candidate_interests_rating]['Общие_интересы'] * interests_coefficient
            music_rating = info[candidate_interests_rating]['Общая_музыка'] * music_coefficient
            movies_rating = info[candidate_interests_rating]['Общие_фильмы'] * movies_coefficient
            books_rating = info[candidate_interests_rating]['Общие_книги'] * books_coefficient
            final_rating = interests_rating + music_rating + movies_rating + books_rating
            sums_of_coefficients.append({candidate_interests_rating: {'candidate_info_rating': final_rating}})

        return sums_of_coefficients

    def search_for_users(self, user_id, age_from, age_to, city_id, query: str):

        if int(age_from) < 18:
            return print('Минимальный возраст для поиска должен быть не менее 18!')

        sex = 1 if self.get_user_info(user_id)['sex'] == 2 else 2
      
        params = {
          'access_token': token,
          'user_id': user_id,
          'v': 5.107,
          'q': query,
          'age_from': age_from,
          'age_to': age_to,
          'sex': sex,
          'status': 6,
          'has_photo': 1,
          'count': 1000,
          'city': city_id,
          'country_id': 1,
          'fields': f'sex, bdate, city, country, domain, \
          relation, activities, interests, music, movies, \
          tv, books, games, about, is_favorite, is_friend, \
          common_count, can_see_audio'
          }

        response = requests.get(f'{API}/users.search', params).json()['response']['items']

        return response

    @classmethod
    def get_city_id(cls, *args) -> int:
        '''Функция для получения id города по его наименованию.
           Первый аргумент city для названия города, второй аргумент
           для региона, кроме Москвы и Санкт-Петербурга.
        '''

        city_id = 0

        params = {
              'access_token': token,
              'v': 5.107,
              'country_id': 1,
              'q': args[0],
              'count': 10
              }
        
        response = requests.get(f'{API}/database.getCities', params).json()

        for item in response['response']['items']:
            if args[0] == 'Москва' or args[0] == 'Санкт-Петербург':
                if 'region' not in item.keys():
                    city_id += item['id']
            else:
                if args[1].capitalize() in item['region']:
                    city_id += item['id']

        return city_id

    def get_top3_photo(self, user_id):

        list_of_photos = []
        
        params = {
                  'access_token': token,
                  'v': 5.107,
                  'owner_id': user_id,
                  'album_id': 'profile',
                  'extended': 1,
                  'count': 200
                  }

        response = requests.get(f'{API}/photos.get', params).json()['response']['items']

        for item in response:
            list_of_photos.append({'user': f'https://vk.com/id{item["owner_id"]}',
                                   'photo_id': item['id'],
                                   'photo_url': item['sizes'][-1]['url'],
                                   'likes': item['likes']})

        for i in range(len(list_of_photos)):
            cursor = list_of_photos[i]
            pos = i
            
            while pos > 0 and list_of_photos[pos - 1]['likes']['count'] < cursor['likes']['count']:
                list_of_photos[pos] = list_of_photos[pos - 1]
                pos = pos - 1
            list_of_photos[pos] = cursor

        return list_of_photos[0:3]

    def add_users_to_db(self):

        print('Для добавления данных в базу введите информацию:')
        with pg.connect(database='vkinder_db', user='rts',
                    password='RVIA2016', host='127.0.0.1',
                    port='5432') as conn:
            cursor = conn.cursor()
            db_functions.delete_table(cursor)
            db_functions.create_db(cursor)

        user_info = self.get_user_info(self.user_id)

        list_of_women_names = ['Мария', 'Анастасия', 'Анна', 'Дарья', 'Елизавета',
                               'Полина', 'Виктория', 'Екатерина', 'Софья', 'Александра']
        list_of_men_names = ['Александр', 'Максим', 'Иван', 'Артем', 'Дмитрий',
                               'Никита', 'Михаил', 'Даниил', 'Егор', 'Андрей']

        list_of_names = []
        users_to_db_list = []

        list_of_names = list_of_women_names if self.get_user_info(self.user_id)['sex'] == 2 else list_of_men_names
        list_of_interests = self.user_text_info_check(list_of_names)

        for user_info in list_of_interests:
            users_to_db_list.append(
                                    {
                                    'vk_id': user_info['id'],
                                    'first_name': user_info['first_name'],
                                    'last_name': user_info['last_name'],
                                    }
                                    )
            
        interests_rating_list = self.get_user_interests_coefficient(list_of_interests)

        for user_info in users_to_db_list:
            for info in interests_rating_list:
                for vk_id, value in info.items():
                    if user_info['vk_id'] == vk_id:
                        user_info.update(value)

    #Добавляем пользователей в базу данных
        with pg.connect(database='vkinder_db', user='rts',
            password='RVIA2016', host='127.0.0.1',
            port='5432') as conn:
            cursor = conn.cursor()
            for candidate in users_to_db_list:
                db_functions.add_user_info_to_db(cursor, candidate)

    def get_top10_users(self):

        print('Выводим данные 10 наиболее перспективных кандидатов:')
    #Выводим фотографии топ-10, затем добавляем их в просмотренные и удаляем из таблицы
    #person info.
        with pg.connect(database='vkinder_db', user='rts',
                password='RVIA2016', host='127.0.0.1',
                port='5432') as conn:
            cursor = conn.cursor()
            viewed_users = []
            list_of_ten = db_functions.get_users(cursor)[0:10]
            top10_photo_info = []
            for item in list_of_ten:
                top10_photo_info.append(self.get_top3_photo(item[1]))
                print(self.get_top3_photo(item[1]))
                db_functions.add_to_viewed(cursor, item[1])
                db_functions.delete_from_db(cursor, item[1])
            print(db_functions.get_users_black_list(cursor))
            with open('candidates.json', 'w', encoding='utf-8') as fo:
                json.dump(top10_photo_info, fo, ensure_ascii=False, indent=4)

    def main(self):

        while True:

            list_of_comands = 'a - добавляет пользователе в базу данных; \n\
s - показывает список из 10 кандидатов;\nq - выход из программы;'
            print(list_of_comands)
            command = input('Введите команду -> ')

            if command == 'a':
                self.add_users_to_db()

            if command == 's':
                self.get_top10_users()

            if command == 'q':
                break

if __name__ == '__main__':

    user = Vkinter('Введите свой vk id', token)
    user.main()
