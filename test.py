import unittest
from Vkinter import Vkinter
import requests

API = 'https://api.vk.com/method'
#Для создания экземпляра класса вносим свой токен
token = ''

class Test(unittest.TestCase):

    def setUp(self):
        self.user = Vkinter('Введите свой vk id', token)
    
    def test_get_user_info(self):

        self.assertEqual('Здесь свой vk id', self.user.get_user_info(self.user.user_id)['id'])

    def test_search_for_users(self):

        self.assertEqual('Мария', self.user.search_for_users(self.user.user_id, 18, 30, 147, 'Мария')[0]['first_name'])
        
    def test_get_city_id(self):

        self.assertEqual(1, self.user.get_city_id('Москва'))
        
if __name__ == '__main__':
    unittest.main()
