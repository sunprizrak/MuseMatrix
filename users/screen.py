from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from .controller import UserController


class AuthScreen(MDScreen):
    core = ObjectProperty()

    def login(self, email, password):
        self.__dict__['user_controller'] = UserController(image=self.core.root.ids.main_screen.image_controller)
        self.user_controller.auth(email=email, password=password, screen=self)
