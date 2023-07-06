from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

storage = JsonStore('storage.json')

host_name = 'https://musematrix.de/'

if platform == 'linux':
    host_name = 'http://127.0.0.1:8000/'

