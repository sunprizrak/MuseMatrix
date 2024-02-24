from kivy.utils import platform
from kivy.clock import mainthread
from kivy import Logger
import json

from kivymd.app import MDApp

if platform == 'android':
    from android import PythonJavaClass, autoclass, java_method, mActivity
    from android.runnable import run_on_ui_thread
    from android import python_act as PythonActivity

    List = autoclass('java.util.List')
    ArrayList = autoclass("java.util.ArrayList")
    context = mActivity.getApplicationContext()
    activity = PythonActivity.mActivity

    BillingClient = autoclass("com.android.billingclient.api.BillingClient")
    KivyPurchasesUpdatedListener = autoclass('org.org.googleplay.KivyPurchasesUpdatedListener')
    KivyBillingClientStateListener = autoclass('org.org.googleplay.KivyBillingClientStateListener')
    KivyProductDetailsResponseListener = autoclass('org.org.googleplay.KivyProductDetailsResponseListener')
    KivyConsumeResponseListener = autoclass('org.org.googleplay.KivyConsumeResponseListener')

    QueryProductDetailsParams = autoclass('com.android.billingclient.api.QueryProductDetailsParams')
    QueryProductDetailsParamsProduct = autoclass('com.android.billingclient.api.QueryProductDetailsParams$Product')
    ProductType = autoclass('com.android.billingclient.api.BillingClient$ProductType')

    BillingFlowParams = autoclass('com.android.billingclient.api.BillingFlowParams')
    BillingFlowParamsProductDetailsParams = autoclass('com.android.billingclient.api.BillingFlowParams$ProductDetailsParams')

    ConsumeParams = autoclass('com.android.billingclient.api.ConsumeParams')


# PurchasesUpdatedListener
class ULCallbackWrapper(PythonJavaClass):
    __javacontext__ = 'app'
    __javainterfaces__ = ['org/org/googleplay/ULCallbackWrapper']

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(Lcom/android/billingclient/api/BillingResult;Ljava/util/List;)V')
    def callback_data(self, billingResult, purchases):
        if self.callback:
            print("ULCallbackWrapper callback_data  True ok")
            self.callback(billingResult, purchases)


# BillingClientStateListener
class SLCallbackWrapper(PythonJavaClass):
    __javacontext__ = 'app'
    __javainterfaces__ = ['org/org/googleplay/SLCallbackWrapper']

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(Lcom/android/billingclient/api/BillingResult;)V')
    def callback_data(self, billingResult):
        if self.callback:
            print("SLCallbackWrapper callback_data  True ok")
            self.callback(billingResult)


# ProductDetailsResponseListener
class DLCallbackWrapper(PythonJavaClass):
    __javacontext__ = 'app'
    __javainterfaces__ = ['org/org/googleplay/DLCallbackWrapper']

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(Ljava/util/List;)V')
    def callback_data(self, productDetails):
        if self.callback:
            print("DLCallbackWrapper callback_data True ok")
            self.callback(productDetails)


# ConsumeResponseListener
class CLCallbackWrapper(PythonJavaClass):
    __javacontext__ = 'app'
    __javainterfaces__ = ['org/org/googleplay/CLCallbackWrapper']

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method("(Lcom/android/billingclient/api/BillingResult;Ljava/lang/String;)V")
    def callback_data(self, billingResult, purchaseToken):
        if self.callback:
            print("CLCallbackWrapper callback_data  True ok")
            self.callback(billingResult, purchaseToken)


class BillingProcessor:
    _billing_client = None
    receiptData = {}

    def __init__(self, _billing_client):
        self._context = context
        self._billing_client = _billing_client
        self.mProductDetails = {}
        self.ul_callback_wrapper = ULCallbackWrapper(self.kivy_purchases_updated_event_handler)
        self.sl_callback_wrapper = SLCallbackWrapper(self.on_billing_setup_finished_event_handler)
        self.dl_callback_wrapper = DLCallbackWrapper(self.on_product_details_response)
        self.cl_callback_wrapper = CLCallbackWrapper(self.on_consume_response)
        self.start_connection()

    @run_on_ui_thread
    def start_connection(self, *args):
        try:
            self.purchases_updated_callback_wrapper = KivyPurchasesUpdatedListener(self.ul_callback_wrapper)
            self.on_billing_setup_finished_callback_wrapper = KivyBillingClientStateListener(self.sl_callback_wrapper)
            self._billing_client = BillingClient.newBuilder(self._context).enablePendingPurchases().setListener(
                self.purchases_updated_callback_wrapper).build()
            self._billing_client.startConnection(self.on_billing_setup_finished_callback_wrapper)

        except Exception as e:
            Logger.info("start_connection exception reason", e)

    @mainthread
    def on_billing_setup_finished_event_handler(self, billingResult):
        if billingResult.getResponseCode() == 0:
            Logger.info('BillingClient setup success')
        else:
            Logger.info("BillingClient setup failed :", billingResult.getResponseCode())

    @mainthread
    def on_consume_response(self, billingResult, purchaseToken):
        if billingResult.getResponseCode() == 0:
            print("OK: The consumable product has been successfully consumed.")
            app = MDApp.get_running_app()
            if self.receiptData:
                purchase_data = json.loads(self.receiptData['purchaseData'])
                product_id = purchase_data.get('productId')

                app = MDApp.get_running_app()
                screen = app.root.get_screen(app.root.current)

                screen.product_purchased(product_id=product_id)

                self.receiptData = {}
            else:
                print("self.receiptData boş")
            return billingResult, purchaseToken
        elif billingResult.getResponseCode() == 1:
            print("USER_CANCELED: The user has canceled the consumption of the consumable product.")
        elif billingResult.getResponseCode() == 2:
            print("SERVICE_UNAVAILABLE: Service Unavailable.")
        elif billingResult.getResponseCode() == 3:
            print("BILLING_UNAVAILABLE: Google Play services are unavailable.")
        elif billingResult.getResponseCode() == 4:
            print("ITEM_ALREADY_OWNED: The user has already purchased the consumable product.")
        elif billingResult.getResponseCode() == 5:
            print("INVALID_ITEM_SKU: The SKU of the consumable is invalid..")
        elif billingResult.getResponseCode() == 6:
            print("INVALID_PURCHASE_TOKEN: The purchase token of the consumable is invalid.")
        elif billingResult.getResponseCode() == 7:
            print("DEVELOPER_ERROR: developer error")
        elif billingResult.getResponseCode() == 8:
            print("ERROR: An unknown error has occurred.")
        else:
            print("There is an uncontrollable situation!!!")

    @mainthread
    def handlePurchase(self, purchase):
        try:
            # google play billing api consumeAsync call
            consume_params = ConsumeParams.newBuilder().setPurchaseToken(purchase.getPurchaseToken()).build()
            listener = KivyConsumeResponseListener(self.cl_callback_wrapper)
            self._billing_client.consumeAsync(consume_params, listener)
        except Exception as e:
            print("handlePurchase exception reason", e)

    @mainthread
    def kivy_purchases_updated_event_handler(self, billingResult, purchases):
        try:
            if billingResult.getResponseCode() == 0 and purchases != None:
                if purchases:
                    for purchase in purchases:
                        # I pass into variable to send receipt data to verify to server
                        self.receiptData = {"purchaseData": purchase.getOriginalJson(),
                                            "signature": purchase.getSignature(),
                                            }
                        self.handlePurchase(purchase)
            elif billingResult.getResponseCode() == 1:
                print("The purchase has been cancelled.")
            else:
                print("Purchase failed")
        except Exception as e:
            print("kivy_purchases_updated_event_handler exception reason", e)

    @mainthread
    def on_product_details_response(self, productDetailsList):
        if productDetailsList:
            for productDetail in productDetailsList:
                product_id = productDetail.getProductId()
                self.mProductDetails[str(product_id)] = productDetail
                # print("Product ID:", productDetail.getProductId())
                # print("Product title:", productDetail.getTitle())
                # print("Product description:", productDetail.getDescription())
                self.launch_billing_flow(product_id)

    @run_on_ui_thread
    def get_purchase_listing_async(self, product_id):
        try:
            product_details_listener = KivyProductDetailsResponseListener(self.dl_callback_wrapper)
            paramsBuilder = QueryProductDetailsParams.newBuilder()
            productBuilder = QueryProductDetailsParamsProduct.newBuilder()
            productBuilder.setProductId(product_id)
            productBuilder.setProductType(ProductType.INAPP)
            productList = productBuilder.build()
            jlist = autoclass('java.util.ArrayList')()
            jlist.add(productList)
            paramsBuilder.setProductList(jlist)
            params = paramsBuilder.build()
            self._billing_client.queryProductDetailsAsync(params, product_details_listener)
        except Exception as e:
            print("get_purchase_listing_async exception reason", e)

    def launch_billing_flow(self, product_id):
        try:
            if product_id in self.mProductDetails:
                productDetails = self.mProductDetails[product_id]
                paramsBuilder = BillingFlowParams.newBuilder()
                productBuilder = BillingFlowParamsProductDetailsParams.newBuilder()
                productBuilder.setProductDetails(productDetails)
                productList = productBuilder.build()
                jlist2 = autoclass('java.util.ArrayList')()
                jlist2.add(productList)
                paramsBuilder.setProductDetailsParamsList(jlist2)
                billingFlowParams = paramsBuilder.build()
                self._billing_client.launchBillingFlow(activity, billingFlowParams)
        except Exception as e:
            print("launch_billing_flow exception reason", e)
