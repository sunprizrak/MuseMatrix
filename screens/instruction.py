from kivymd.uix.transition import MDSwapTransition

from .layout import BaseScreen
from kivy.utils import platform


class InstructionScreen(BaseScreen):

    # def on_pre_enter(self, *args):
    #     if platform == 'android':
    #         color_nav = self.theme_cls.primary_color
    #         self.app.change_android_color(color_nav=color_nav)
    #
    # def on_pre_leave(self, *args):
    #     if platform == 'android':
    #         self.app.change_android_color()

    def move_to_screen(self, instance, value):
        if value == 'Purchase via google play store':
            self.app.root.transition = MDSwapTransition()
            self.app.root.current = 'buy_coins_screen'
        elif value == 'View ads':
            self.app.root.ids.main_screen.show_ads()