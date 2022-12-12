from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from users.auth import Auth

from users.screen import AuthScreen
from main.screen import MainScreen, OpenImageScreen


import openai

Window.size = (360, 600)


class ArtAIApp(MDApp):

    def __init__(self, **kwargs):
        super(ArtAIApp, self).__init__(**kwargs)
        self.auth = Auth()
        self.dialog = None
        self.theme_cls.material_style = 'M3'

    def build(self):
        kv_file = Builder.load_file('./kv/layout.kv')
        return kv_file

    def show_dialog(self):
        self.dialog = MDDialog(
            title='Notice!',
            type='custom',
            buttons=[
                MDFlatButton(
                    text="Close",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.close_dialog,
                ),
            ],
        )
        self.dialog.open()

    def close_dialog(self, inst):
        self.dialog.dismiss()


if __name__ == '__main__':
    ArtAIApp().run()