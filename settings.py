from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

storage = JsonStore('storage.json')

host_name = 'http://3.231.178.17:80/'

if platform == 'linux':
    host_name = 'http://127.0.0.1:8000/'


GOOGLE_REDIRECT_URL = host_name + '/users/google_complete/'

