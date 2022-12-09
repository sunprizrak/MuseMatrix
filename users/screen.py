from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import FallOutTransition
from kivymd.uix.screen import MDScreen
from .auth import Auth
from .controller import UserController


class AuthScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(AuthScreen, self).__init__(**kwargs)
        self.auth = Auth()

    def login(self, email, password):

        def load_data():
            self.user_controller.get_data_user()

        login = self.auth(email, password)
        if self.auth.is_auth():
            self.__dict__['user_controller'] = UserController(login)
            load_data()
            self.ids.email_field.text = ''
            self.ids.password_field.text = ''
            self.parent.transition = FallOutTransition()
            self.parent.current = 'create_screen'
        else:
            self.core.show_dialog()
            self.core.dialog.text = login