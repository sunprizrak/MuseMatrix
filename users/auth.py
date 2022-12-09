import requests


class Auth:
    host_name = 'http://127.0.0.1:8000/'
    path_login = host_name + 'auth/token/login/'
    path_logout = host_name + 'auth/token/logout/'

    def __init__(self):
        self.session = requests.Session()
        self.switch = False

    def __get_token(self, email, password):
        response = self.session.post(url=self.path_login, data={'email': email, 'password': password})
        if response.status_code == 200:
            value = response.json().get('auth_token')
            self.session.headers = {'Authorization': f'Token {value}'}
            self.switch = True

    def del_token(self):
        try:
            self.session.post(url=self.path_logout, headers={'Authorization': f'Token {self.token}'})
        except requests.RequestException as e:
            self.session.close()
            self.switch = False
        self.session.close()
        self.switch = False

    def is_auth(self):
        return self.switch

    def __call__(self, email, password):
        try:
            self.__get_token(email=email, password=password)
            if self.is_auth():
                return self.session
            else:
                return 'Email or password entered incorrectly'
        except requests.RequestException as e:
            return 'Problem with connection'''

