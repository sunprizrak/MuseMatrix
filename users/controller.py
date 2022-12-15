from kivy.network.urlrequest import UrlRequest
from kivy.cache import Cache
import json
from kivy.uix.screenmanager import FallOutTransition

from .models import User
from main.controller import ImageController


class UserController:
    user = User()
    host_name = 'http://127.0.0.1:8000/'
    path_login = host_name + 'auth/token/login/'
    path_logout = host_name + 'auth/token/logout/'
    path_data_user = host_name + 'auth/users/me/'

    def __init__(self, screen):
        self.screen = screen
        self.image_controller = ImageController(screen=screen)

    def auth(self, email, password):

        def output_error(error):
            if type(error) is str:
                self.screen.core.show_dialog()
                self.screen.core.dialog.text = error
            elif type(error) is dict:
                if len({'password', 'email'} & set(error)) > 0:
                    print('password or email обработать поля')
                else:
                    error_text = ''
                    for value in error.values():
                        error_text += f'{value[0]}\n'
                    self.screen.core.show_dialog()
                    self.screen.core.dialog.text = error_text

        def callback(request, response):
            Cache.register('token', limit=None, timeout=None)
            Cache.append('token', 'auth_token', response.get('auth_token'))

            self.get_data_user()
            self.image_controller.get_image_list()

            self.screen.ids.email_field.text = ''
            self.screen.ids.password_field.text = ''
            self.screen.parent.transition = FallOutTransition()
            self.screen.parent.current = 'main_screen'

        def callback_failure(request, response):
            output_error(error=response)

        def callback_error(request, error):
            output_error(error=error)

        UrlRequest(
            url=self.path_login,
            method='POST',
            on_success=callback,
            on_error=callback_error,
            on_failure=callback_failure,
            req_headers={'Content-type': 'application/json'},
            req_body=json.dumps({'email': email, 'password': password}),
        )

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
                         'Authorization': f'Token {"token"}',
                         },
        )

