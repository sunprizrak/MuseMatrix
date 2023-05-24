from kivy.storage.jsonstore import JsonStore

storage = JsonStore('storage.json')

host_name =  'http://127.0.0.1:8000/' #'http://3.231.178.17:80/'

# Google Play console

PLAY_CONSOLE_KEY = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAgZRRyPl6ONDuO/g1mQhcI2JAxpJ8+vmOKqIk/zMUj8nvKkDFAoI9RoUR19hdyvI3bO0NK5j1snhRjdahXyE90BjwU9QT/Ol7yBhuvrbdfEQQ/0S9P3MSjZys0NDMaLpsX9Sa7WNPcn7Tdxg0oJ85F562nUyqcdUbjGqzEgGmKtqewYNUOve5hHxGJkmwblma40CriCi+tsjYgVigO669GBvy0ENN1Wml1+v+LYwFB6EjTRL5rViaokJUAl2haaS8zwaSBrc/ykQuGBVe/9dEci2quUUVK7PXxdo3ivKwXrIKCeaHvI66l22jei5wmoNCH6KHmIlWMOit1T5LzJmkPwIDAQAB'

GOOGLE_REDIRECT_URL = host_name + '/users/google_complete/'

