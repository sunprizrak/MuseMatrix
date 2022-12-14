from kivy.cache import Cache
from kivy.network.urlrequest import UrlRequest
import json


class Auth:
    host_name = 'http://127.0.0.1:8000/'
    path_login = host_name + 'auth/token/login/'
    path_logout = host_name + 'auth/token/logout/'

    def __get_token(self, email, password):

        def callback(request, response):
            Cache.register('token', limit=None, timeout=None)
            Cache.append('token', 'auth_token', response.get('auth_token'))

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
        )

    def del_token(self):

        def callback(request, response):
            pass

        def callback_failure(request, response):
            pass

        UrlRequest(
            url=self.path_logout,
            method='POST',
            on_success=callback,
            on_failure=callback_failure,
            req_headers={'Content-type': 'application/json',
                         'Authorization': f'Token {self.token}',
                         },
        )

