from kivy.storage.jsonstore import JsonStore

storage = JsonStore('settings.json')

host_name = 'http://18.214.87.35:8000/'  # 'http://127.0.0.1:8000/'

google_redirect_url = host_name + '/users/google_complete/'