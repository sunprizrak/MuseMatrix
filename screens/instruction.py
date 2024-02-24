from kivymd.uix.transition import MDSwapTransition
from .layout import BaseScreen


class InstructionScreen(BaseScreen):
    def move_to_screen(self, instance, value):
        if value == 'Purchase via google play store':
            self.app.root.transition = MDSwapTransition()
            self.app.root.current = 'buy_coins_screen'
        elif value == 'View ads':
            self.app.root.ids.main_screen.show_ads()