from kivymd.app import MDApp
from kivy.core.window import Window
from create_screen import CreateScreen
from open_image_screen import OpenImageScreen

Window.size = (360, 600)


class MainApp(MDApp):
    pass


if __name__ == '__main__':
    MainApp().run()