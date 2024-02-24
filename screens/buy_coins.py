from controller.user import UserController
from .layout import BaseScreen
from kivy.utils import platform

if platform == 'android':
    from googleplayapi import BillingProcessor
    from kivymd.toast import toast


class BuyCoinsScreen(BaseScreen):
    PROD_200 = 'a134b'
    PROD_400 = 'a135b'
    PROD_1000 = 'a136b'
    PROD_1600 = 'a137b'
    PROD_3600 = 'a138b'
    PROD_5000 = 'a139b'
    PROD_20000 = 'a140b'

    products = [PROD_200, PROD_400, PROD_1000, PROD_1600, PROD_3600, PROD_5000, PROD_20000]

    amounts = {PROD_200: 200, PROD_400: 400, PROD_1000: 1000, PROD_1600: 1600, PROD_3600: 3600, PROD_5000: 5000, PROD_20000: 20000}

    def __init__(self, **kwargs):
        super(BuyCoinsScreen, self).__init__(**kwargs)
        self.user_controller = UserController()

    def on_pre_enter(self, *args):
        if platform == 'android':
            if not hasattr(self, 'bp'):
                setattr(self, 'bp', BillingProcessor(
                    self.user_controller.user.play_console_key,
                ))

    def open_payment_layout(self, sku):
        setattr(self, 'product_id', sku)
        self.ids.bottom_sheet.set_state('toggle')

    def initiate_purchase(self, method_name):
        if platform == 'android':
            if method_name == "gplay":
                if self.product_id in self.products:
                    # get and purchase
                    self.bp.get_purchase_listing_async(self.product_id)
            else:
                toast(
                    text="Payment method not implemented",
                    length_long=True,
                    gravity=40,
                    y=self.top,
                )

    def product_purchased(self, product_id):
        total_amount = self.user_controller.user.coin + self.amounts.get(product_id)

        def _on_success(request, response):
            self.user_controller.user.update(data_user=response)
            screen = self.app.root.get_screen('main_screen')
            screen.coin = self.user_controller.user.coin

        self.user_controller.update_user(fields={'coin': total_amount}, on_success=_on_success)

        self.ids.bottom_sheet.set_state("toggle")