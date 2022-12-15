from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from .controller import UserController


class AuthScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(AuthScreen, self).__init__(**kwargs)
        self.user_controller = UserController(screen=self)

    def login(self, email, password):
        self.user_controller.auth(email=email, password=password)
