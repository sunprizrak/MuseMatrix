from kivy import Logger
from controller.user import UserController
from .layout import BaseScreen
from kivy.utils import platform

if platform == 'android':
    from iabwrapper import BillingProcessor
    from kivymd.toast import toast


class BuyCoinsScreen(BaseScreen):
    PROD_200 = 'a134b'
    PROD_400 = 'a135b'
    PROD_1000 = 'a136b'
    PROD_1600 = 'a137b'
    PROD_3600 = 'a138b'
    PROD_5000 = 'a139b'
    PROD_20000 = 'a140b'
    PROD_MONTHLY_1 = "one_month"
    PROD_ANNUAL_1 = "one_year"

    products = [PROD_200, PROD_400, PROD_1000, PROD_1600, PROD_3600, PROD_5000, PROD_20000]
    subscriptions = [PROD_MONTHLY_1, PROD_ANNUAL_1]

    amounts = {PROD_200: 200, PROD_400: 400, PROD_1000: 1000, PROD_1600: 1600, PROD_3600: 3600, PROD_5000: 5000, PROD_20000: 20000}

    def __init__(self, **kwargs):
        super(BuyCoinsScreen, self).__init__(**kwargs)
        self.user_controller = UserController()

    def on_pre_enter(self, *args):
        if platform == 'android':
            if not hasattr(self, 'bp'):
                setattr(self, 'bp', BillingProcessor(self.user_controller.user.play_console_key, self.product_purchased, self.billing_error,
                                                     onBillingInitializedMethod=self.billing_initialized))

            Logger.info(f"is_initialized: {self.bp.is_initialized()}")
            Logger.info(f'is_iab_service_available: {self.bp.is_iab_service_available()}')
            Logger.info(f"is_subscription_update_supported: {self.bp.is_subscription_update_supported()}")

            owned_products = self.bp.list_owned_products()
            owned_subscriptions = self.bp.list_owned_subscriptions()

            for product in owned_products:
                Logger.info(f"Product: {product}")

            for subscription in owned_subscriptions:
                Logger.info(f"Subscription: {subscription}")

    def open_payment_layout(self, sku):
        if platform == 'android':
            if self.bp.is_subscribed(sku):
                toast(
                    text="Already Subscribed",
                    length_long=True,
                    gravity=40,
                    y=self.top,
                    x=0,
                )
                return
        setattr(self, 'product_id', sku)
        self.ids.bottom_sheet.set_state('toggle')

    def initiate_purchase(self, method_name):
        if platform == 'android':
            if method_name == "gplay":
                if self.product_id in self.products:
                    # Get Details about a product
                    self.bp.get_purchase_listing_async(self.product_id, self.purchase_details_received)
                    self.bp.purchase_product(self.product_id)
                elif self.product_id in self.subscriptions:
                    # Get Details about a subscription
                    self.bp.get_subscription_listing_async(self.product_id, self.purchase_details_received)
                    self.bp.subscribe_product(self.product_id)
            else:
                toast(
                    text="Payment method not implemented",
                    length_long=True,
                    gravity=40,
                    y=self.top,
                    x=0,
                )

    def product_purchased(self, product_id, purchase_info):
        if platform == 'android':
            toast(
                text="Product purchased",
                length_long=True,
                gravity=40,
                y=self.top,
                x=0,
            )


        total_amount = self.user_controller.user.coin + self.amounts.get(product_id)

        def _on_success(request, response):
            self.user_controller.user.update(data_user=response)
            screen = self.app.root.get_screen('main_screen')
            screen.coin = self.user_controller.user.coin

        self.user_controller.update_user(fields={'coin': total_amount}, on_success=_on_success)

        self.ids.bottom_sheet.dismiss()

    def billing_error(self, error_code, error_message):
        Logger.info("Billing error")

    def billing_initialized(self):
        Logger.info("Billing initialized")

    def purchase_details_received(self, product_info):
        if product_info.size() != 0:
            product_info = product_info[0]
            details = {
                "productId": product_info.productId,
                "title": product_info.title,
                "description": product_info.description,
                "isSubscription": product_info.isSubscription,
                "currency": product_info.currency,
                "priceValue": product_info.priceValue,
                "priceText": product_info.priceText,
            }
            Logger.info(details)
        else:
            if platform == 'android':
                toast(
                    text="No purchase details received",
                    length_long=True,
                    gravity=40,
                    y=self.top,
                    x=0,
                )