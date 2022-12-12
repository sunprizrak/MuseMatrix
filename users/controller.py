from kivy.network.urlrequest import UrlRequest
from kivy.cache import Cache

from .models import User


class UserController:
    user = User()
    host_name = 'http://127.0.0.1:8000/'
    path_data_user = host_name + 'auth/users/me/'

    def get_data_user(self):

        def callback(request, response):
            self.user.update(data_user=response)

        UrlRequest(
            url=self.path_data_user,
            method='GET',
            on_success=callback,
            req_headers={'Content-type': 'application/json',
                         'Authorization': f"Token {Cache.get('token', 'auth_token')}",
                         },
        )