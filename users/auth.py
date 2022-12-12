from kivy.cache import Cache
from kivy.network.urlrequest import UrlRequest
import json


class Auth:
    host_name = 'http://127.0.0.1:8000/'
    path_login = host_name + 'auth/token/login/'
    path_logout = host_name + 'auth/token/logout/'

    def __init__(self):
        self.switch = False
        self.error = None

    def __get_token(self, email, password):

        def callback(request, response):
            Cache.register('token', limit=None, timeout=None)
            Cache.append('token', 'auth_token', response.get('auth_token'))
            self.switch = True

        def callback_failure(request, response):
            self.error = response

        def callback_error(request, error):
            self.error = error.strerror

        UrlRequest(
            url=self.path_login,
            method='POST',
            on_success=callback,
            on_error=callback_error,
            on_failure=callback_failure,
            req_headers={'Content-type': 'application/json'},
            req_body=json.dumps({'email': email, 'password': password}),
        ).wait()

    def del_token(self):

        def callback(request, response):
            self.switch = False

        def callback_failure(request, response):
            self.switch = False

        UrlRequest(
            url=self.path_logout,
            method='POST',
            on_success=callback,
            on_failure=callback_failure,
            req_headers={'Content-type': 'application/json',
                         'Authorization': f'Token {self.token}',
                         },
        )

    def is_auth(self):
        return self.switch

    def __call__(self, email, password):
        self.__get_token(email=email, password=password)

        if self.is_auth():
            return True
        else:
            return self.error
