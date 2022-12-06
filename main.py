from kivymd.app import MDApp
from kivy.core.window import Window
import openai
from create_screen import CreateScreen
from open_image_screen import OpenImageScreen

Window.size = (360, 600)


class MainApp(MDApp):

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        openai.api_key = ''


if __name__ == '__main__':
    MainApp().run()