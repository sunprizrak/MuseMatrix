from kivy.storage.jsonstore import JsonStore

storage = JsonStore('storage.json')

host_name = 'http://3.231.178.17:80/' #'http://127.0.0.1:8000/'

google_redirect_url = host_name + '/users/google_complete/'

credit_one_generate = 20