from kivy.uix.screenmanager import FallOutTransition
from kivymd.uix.screen import MDScreen


class OpenImageScreen(MDScreen):

    def back(self, screen):
        self.parent.transition = FallOutTransition()
        self.parent.current = screen