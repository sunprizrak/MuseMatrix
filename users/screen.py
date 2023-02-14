from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from .controller import UserController


class LoginScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.user_controller = UserController(screen=self)

    def login(self, email, password):
        self.user_controller.auth(email=email, password=password)


class RegistrateScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(RegistrateScreen, self).__init__(**kwargs)
        self.user_controller = UserController(screen=self)

    def registrate(self, email, password, re_password):
        self.user_controller.registrate(email=email, password=password, re_password=re_password)


class ChangePasswordScreen(MDScreen):

    def __init__(self, **kwargs):
        super(ChangePasswordScreen, self).__init__(**kwargs)
        self.user_controller = UserController(screen=self)

    def change_password(self, current_password, new_password, re_new_password):
        self.user_controller.set_password(current_password=current_password, new_password=new_password, re_new_password=re_new_password)



