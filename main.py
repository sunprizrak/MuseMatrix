from kivymd.app import MDApp
from kivy.core.window import Window
from generate_screen import ImageSection, OptionSection

Window.size = (360, 600)


class MainApp(MDApp):
    pass


if __name__ == '__main__':
    MainApp().run()