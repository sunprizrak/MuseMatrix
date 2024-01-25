from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import NoTransition, FallOutTransition
from kivymd.app import MDApp
from kivymd.uix.transition.transition import MDSwapTransition
from models import User
from controller.image import ImageController
import json
from settings import host_name


class UserController:
    user = User()
    path_reg = host_name + 'auth/users/'
    path_login = host_name + 'auth/token/login/'
    path_logout = host_name + 'auth/token/logout/'
    path_data_user = host_name + 'auth/users/me/'
    path_set_password = host_name + 'auth/users/set_password/'
    path_reset_password = host_name + 'auth/users/reset_password/'
    path_google_oauth2 = host_name + 'auth/o/google-oauth2/'
    path_resend_activation = host_name + 'auth/users/resend_activation/'
    path_google_redirect = host_name + 'users/google_complete/'

    def __init__(self):
        self.app = MDApp.get_running_app()
        self.image_controller = ImageController()

    def registrate(self, *args, **kwargs):

        UrlRequest(
            url=self.path_reg,
            method='POST',
            on_success=kwargs.get('on_success'),
            on_error=kwargs.get('on_error'),
            on_failure=kwargs.get('on_failure'),
            req_headers={'Content-type': 'application/json'},
            req_body=json.dumps({
                'email': kwargs.get('email'),
                'password': kwargs.get('password'),
                're_password': kwargs.get('re_password'),
            }),
        )

    def resend_activation(self, *args, **kwargs):

        UrlRequest(
            url=self.path_resend_activation,
            method='POST',
            on_success=kwargs.get('on_success'),
            req_headers={'Content-type': 'application/json'},
            req_body=json.dumps({'email': kwargs.get('email')}),
        )

    def auth(self, *args, **kwargs):

        UrlRequest(
            url=self.path_login,
            method='POST',
            on_success=kwargs.get('on_success'),
            on_error=kwargs.get('on_error'),
            on_failure=kwargs.get('on_failure'),
            req_headers={'Content-type': 'application/json'},
            req_body=json.dumps({
                'email': kwargs.get('email'),
                'password': kwargs.get('password')
            }),
        )

    def authorized(self):
        self._get_data_user()
        # self.image_controller.get_image_list()

        if self.app.root.current == 'login_screen':
            self.app.root.transition = MDSwapTransition()
        else:
            self.app.root.transition = NoTransition()

        self.app.root.current = 'main_screen'

    def google_oauth2(self, *args, **kwargs):

        def _on_failure(request, response):
            print(response)

        def _on_error(request, error):
            print(error)

        UrlRequest(
            url=f'{self.path_google_oauth2}?redirect_uri={self.path_google_redirect}',
            method='GET',
            on_failure=_on_failure,
            on_error=_on_error,
            on_success=kwargs.get('on_success'),
        )

    def _get_data_user(self):

        def _on_success(request, response):
            self.user.update(data_user=response)
            screen = self.app.root.get_screen('main_screen')
            screen.email = self.user.email
            screen.coin = self.user.coin
            screen.avatar = self.user.avatar
            screen.chat_token = self.user.chat_token

        UrlRequest(
            url=self.path_data_user,
            method='GET',
            on_success=_on_success,
            req_headers={'Content-type': 'application/json',
                         'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
                         },
        )

    def update_user(self, *args, **kwargs):

        req_body = json.dumps(kwargs.get('fields'))

        UrlRequest(
            url=self.path_data_user,
            method='PATCH',
            on_success=kwargs.get('on_success'),
            req_headers={'Content-type': 'application/json',
                         'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
                         },
            req_body=req_body,
        )

    def set_password(self, *args, **kwargs):

        UrlRequest(
            url=self.path_set_password,
            method='POST',
            on_success=kwargs.get('on_success'),
            on_error=kwargs.get('on_error'),
            on_failure=kwargs.get('on_failure'),
            req_headers={'Content-type': 'application/json',
                         'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
                         },
            req_body=json.dumps({'new_password': kwargs.get('new_password'),
                                 're_new_password': kwargs.get('re_new_password'),
                                 'current_password': kwargs.get('current_password'),
                                 }),
        )

    def reset_password(self, email):

        def _output_error(error):
            if type(error) is dict:
                self.app.dialog.dismiss()
                error_text = ''
                for value in error.values():
                    error_text += f'{value[0]}\n'
                self.app.show_dialog()
                self.app.dialog.text = error_text

        def _on_success(request, response):
            self.app.dialog.dismiss()

        def _on_failure(request, response):
            _output_error(response)

        def _on_error(request, error):
            _output_error(error)

        UrlRequest(
            url=self.path_reset_password,
            method='POST',
            on_success=_on_success,
            on_error=_on_error,
            on_failure=_on_failure,
            req_headers={'Content-type': 'application/json'},
            req_body=json.dumps({'email': email}),
        )

    def un_login(self):
        if self.app.storage.exists('auth_token'):
            self._del_token()
            self.app.storage.delete('auth_token')

            self.image_controller.clear_image_list()

            self.app.root.transition = FallOutTransition()
            self.app.root.current = 'start_screen'

    def _del_token(self):

        UrlRequest(
            url=self.path_logout,
            method='POST',
            req_headers={'Content-type': 'application/json',
                         'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
                         },
        )

