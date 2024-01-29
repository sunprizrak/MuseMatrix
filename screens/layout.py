from kivy.utils import platform
from kivy.properties import BoundedNumericProperty, StringProperty, NumericProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from controller.openai import OpenAIController
from controller.user import UserController


class BaseScreen(MDScreen):
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.theme_bg_color = 'Custom'


class ImageScreen(BaseScreen):
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty()
    price = NumericProperty()

    def __init__(self, **kwargs):
        super(ImageScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.user_controller = UserController()

    # def on_pre_enter(self, *args):
    #     if platform == 'android':
    #         color_nav = self.theme_cls.primary_color
    #         self.app.change_android_color(color_nav=color_nav)
    #
    # def on_pre_leave(self, *args):
    #     if platform == 'android':
    #         self.app.change_android_color()