from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import NoTransition, FallOutTransition
from kivymd.uix.transition.transition import MDSwapTransition
from models import User
from controller.image import ImageController
import json
from settings import storage, host_name, GOOGLE_REDIRECT_URL


class UserController:
    user = User()
    path_reg = host_name + 'auth/users/'
    path_login = host_name + 'auth/token/login/'
    path_logout = host_name + 'auth/token/logout/'
    path_data_user = host_name + 'auth/users/me/'
    path_set_password = host_name + 'auth/users/set_password/'
    path_reset_password = host_name + 'auth/users/reset_password/'
    path_google_oauth2 = host_name + 'auth/o/google-oauth2/'

    def __init__(self, screen):
        self.screen = screen
        self.image_controller = ImageController(screen=screen)

    def registrate(self, email, password, re_password):

        def output_error(error):
            if type(error) is str:
                self.screen.core.show_dialog()
                self.screen.core.dialog.text = error
            elif type(error) is dict:
                if {'email', 'password', 're_password'} & set(error):
                    for el in {'email', 'password', 're_password'} & set(error):
                        error_text = error.get(el)[0]
                        field = self.screen.ids.get(f'{el}_field')
                        field.error = True
                        field.helper_text = error_text
                elif {'non_field_errors'} & set(error):
                    error_text = error.get('non_field_errors')[0]
                    for el in self.screen.ids:
                        if 'password' in el:
                            field = self.screen.ids.get(f'{el}')
                            field.error = True
                            field.helper_text = error_text
                else:
                    error_text = ''
                    for value in error.values():
                        error_text += f'{value[0]}\n'
                    self.screen.core.show_dialog()
                    self.screen.core.dialog.text = error_text

        def callback(request, response):
            self.screen.parent.current = 'login_screen'
            self.screen.core.show_dialog()
            self.screen.core.dialog.title = 'success!'
            self.screen.core.dialog.text = 'Login with email and password'

        def callback_failure(request, response):
            output_error(error=response)

        def callback_error(request, error):
            output_error(error=error)

        UrlRequest(
            url=self.path_reg,
            method='POST',
            on_success=callback,
            on_error=callback_error,
            on_failure=callback_failure,
            req_headers={'Content-type': 'application/json'},
            req_body=json.dumps({'email': email, 'password': password, 're_password': re_password}),
        )

    def auth(self, email, password):

        def output_error(error):
            if type(error) is str:
                self.screen.core.show_dialog()
                self.screen.core.dialog.text = error
            elif type(error) is dict:
                if len({'password', 'email'} & set(error)) > 0:
                    for el in {'password', 'email'} & set(error):
                        error_text = error.get(el)[0]
                        field = self.screen.ids.get(f'{el}_field')
                        field.error = True
                        field.helper_text = error_text
                else:
                    error_text = ''
                    for value in error.values():
                        error_text += f'{value[0]}\n'
                    self.screen.core.show_dialog()
                    self.screen.core.dialog.text = error_text

        def callback(request, response):

            storage.put('auth_token', token=response.get('auth_token'))

            self.get_data_user()
            self.image_controller.get_image_list()

            self.screen.parent.transition = MDSwapTransition()
            self.screen.parent.current = 'main_screen'

        def callback_failure(request, response):
            output_error(error=response)
            print(response)

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

    def authorized(self):
        self.get_data_user()
        self.image_controller.get_image_list()

        self.screen.parent.transition = NoTransition()
        self.screen.parent.current = 'main_screen'

    def google_oauth2(self, callback):

        UrlRequest(
            url=f'{self.path_google_oauth2}?redirect_uri={GOOGLE_REDIRECT_URL}',
            method='GET',
            on_success=callback,
            #on_error=callback_error,
            #on_failure=callback_failure,
            req_headers={'Content-type': 'application/json'},
        )

    def un_login(self):
        if storage.exists('auth_token'):
            storage.delete('auth_token')

            self.image_controller.clear_image_list(self.screen.core.root.ids.collection_screen.ids.selection_list.children)

            self.screen.core.root.transition = FallOutTransition()
            self.screen.core.root.current = 'start_screen'

    def get_data_user(self):

        def callback(request, response):
            self.user.update(data_user=response)
            self.screen.core.root.ids.main_screen.email = self.user.email
            self.screen.core.root.ids.main_screen.coin = self.user.coin
            self.screen.core.root.ids.main_screen.avatar = self.user.avatar
            self.screen.core.root.ids.main_screen.chat_token = self.user.chat_token

        UrlRequest(
            url=self.path_data_user,
            method='GET',
            on_success=callback,
            req_headers={'Content-type': 'application/json',
                         'Authorization': f"Token {storage.get('auth_token').get('token')}",
                         },
        )

    def update_user(self, field_name, field_value):

        def callback(request, response):
            self.user.update(data_user=response)

        req_body = json.dumps({field_name: field_value})

        UrlRequest(
            url=self.path_data_user,
            method='PATCH',
            on_success=callback,
            req_headers={'Content-type': 'application/json',
                         'Authorization': f"Token {storage.get('auth_token').get('token')}",
                         },
            req_body=req_body,
        )

    def set_password(self, current_password, new_password, re_new_password):

        def output_error(error):
            if type(error) is str:
                self.screen.core.show_dialog()
                self.screen.core.dialog.text = error
            elif type(error) is dict:
                if {'current_password', 'new_password', 're_new_password'} & set(error):
                    for el in {'current_password', 'new_password', 're_new_password'} & set(error):
                        error_text = error.get(el)[0]
                        field = self.screen.ids.get(f'{el}_field')
                        field.error = True
                        field.helper_text = error_text
                elif {'non_field_errors'} & set(error):
                    error_text = error.get('non_field_errors')[0]
                    for el in self.screen.ids:
                        if 'new_password' in el:
                            field = self.screen.ids.get(f'{el}')
                            field.error = True
                            field.helper_text = error_text
                else:
                    error_text = ''
                    for value in error.values():
                        error_text += f'{value[0]}\n'
                    self.screen.core.show_dialog()
                    self.screen.core.dialog.text = error_text

        def callback(request, response):
            self.screen.core.show_dialog()
            self.screen.core.dialog.title = 'success!'
            self.screen.core.dialog.text = 'Password has been successfully changed!'

        def callback_failure(request, response):
            output_error(error=response)

        def callback_error(request, error):
            output_error(error=error)

        UrlRequest(
            url=self.path_set_password,
            method='POST',
            on_success=callback,
            on_error=callback_error,
            on_failure=callback_failure,
            req_headers={'Content-type': 'application/json',
                         'Authorization': f"Token {storage.get('auth_token').get('token')}",
                         },
            req_body=json.dumps({'new_password': new_password,
                                 're_new_password': re_new_password,
                                 'current_password': current_password,
                                 }),
        )

    def reset_password(self, email):

        def output_error(error):
            if type(error) is dict:
                self.screen.core.dialog.dismiss()
                error_text = ''
                for value in error.values():
                    error_text += f'{value[0]}\n'
                self.screen.core.show_dialog()
                self.screen.core.dialog.text = error_text

        def callback(request, response):
            self.screen.core.dialog.dismiss()

        def callback_failure(request, response):
            output_error(error=response)

        def callback_error(request, error):
            output_error(error=error)

        UrlRequest(
            url=self.path_reset_password,
            method='POST',
            on_success=callback,
            on_error=callback_error,
            on_failure=callback_failure,
            req_headers={'Content-type': 'application/json'},
            req_body=json.dumps({'email': email}),
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

