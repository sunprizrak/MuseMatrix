from kivy.utils import platform

host_name = 'https://musematrix.de/'

if platform == 'linux':
    host_name = 'http://127.0.0.1:8000/'

