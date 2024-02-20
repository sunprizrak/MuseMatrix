from kivy.properties import StringProperty, NumericProperty
from kivy.utils import platform
from kivymd.uix.transition import MDSwapTransition
from controller.user import UserController
from .layout import BaseScreen


class MainScreen(BaseScreen):
    email = StringProperty('email')
    coin = NumericProperty()
    chat_token = NumericProperty()
    avatar = StringProperty('avatar')

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.user_controller = UserController()

    def add_chat_token(self):
        def _on_success(request, response):
            self.user_controller.user.update(data_user=response)
            self.coin = self.user_controller.user.coin
            self.chat_token = self.user_controller.user.chat_token

        if self.coin > 0:
            data = {'coin': self.coin - 1, 'chat_token': self.chat_token + 1000}
            self.user_controller.update_user(fields=data, on_success=_on_success)
        else:
            self.app.show_dialog()
            self.app.dialog.title = 'Notice!'
            self.app.dialog.text = 'Not enough coins. Replenishment requires 1 coin(1 coin = 1000 chat tokens)'

    def show_ads(self):
        if platform == 'android':
            self.app.reward_interstitial.show()

    def open_settings(self):
        self.ids.nav_drawer.set_state("close")
        self.app.root.transition = MDSwapTransition()
        self.app.root.current = 'settings_screen'

    def open_collection(self):
        self.ids.nav_drawer.set_state("close")
        self.app.root.transition = MDSwapTransition()
        self.app.root.current = 'collection_screen'

    def open_buy_credits(self):
        self.ids.nav_drawer.set_state('close')
        self.app.root.transition = MDSwapTransition()
        self.app.root.current = 'buy_coins_screen'

    def exit(self):
        self.ids.nav_drawer.set_state("close")
        self.user_controller.un_login()