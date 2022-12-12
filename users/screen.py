from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import FallOutTransition
from kivymd.uix.screen import MDScreen
from .controller import UserController


class AuthScreen(MDScreen):
    core = ObjectProperty()

    def login(self, email, password):

        def load_data():
            self.user_controller.get_data_user()

        login = self.core.auth(email, password)

        if self.core.auth.is_auth():
            self.__dict__['user_controller'] = UserController()
            load_data()
            self.ids.email_field.text = ''
            self.ids.password_field.text = ''
            self.parent.transition = FallOutTransition()
            self.parent.current = 'main_screen'
        else:
            if type(login) is str:
                self.core.show_dialog()
                self.core.dialog.text = login
            elif type(login) is dict:
                if len({'password', 'email'} & set(login)) > 0:
                    print('password or email обработать поля')
                else:
                    error = ''
                    for value in login.values():
                        error += f'{value[0]}\n'
                    self.core.show_dialog()
                    self.core.dialog.text = error

