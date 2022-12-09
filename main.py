from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from image.screen import CreateScreen, OpenImageScreen
from users.screen import AuthScreen
import openai

Window.size = (360, 600)


class MainApp(MDApp):

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.dialog = None
        print(dir(self))
        openai.api_key = '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'

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
    MainApp().run()