from kivy import Logger
from kivy.core.window import Window
from kivy.metrics import sp, dp
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import FallOutTransition
from kivy.properties import StringProperty, ObjectProperty, BoundedNumericProperty, NumericProperty
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.chip import MDChip
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.swiper import MDSwiperItem, MDSwiper
from kivy.core.image import Image as CoreImage
from kivymd.uix.textfield import MDTextField
from kivymd.uix.transition import MDSwapTransition
import settings
from widgets import MyImage
import io
import base64
import uuid
from os.path import join, exists
from PIL import Image as PilImage
from kivy.utils import platform
from controller.user import UserController
from controller.openai import OpenAIController
from controller.image import ImageController
import logging
import tiktoken

if platform == 'android':
    from iabwrapper import BillingProcessor

logging.getLogger('PIL').setLevel(logging.WARNING)


class StartScreen(MDScreen):
    core = ObjectProperty()


class LoginScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.user_controller = UserController(screen=self)

    def on_pre_leave(self, *args):
        for field_name in self.ids.keys():
            if 'field' in field_name:
                self.ids[field_name].text = ''

    def login(self, email, password):
        self.user_controller.auth(email=email, password=password)

    def google_login(self):

        def callback(request, response):
            url = response.get('authorization_url')
            self.core.view_browser(url=url)

        self.user_controller.google_oauth2(callback=callback)

    def forgot_password(self):

        content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height="50dp",
        )

        email_field = MDTextField(
            hint_text='Email',
            mode="rectangle",
        )

        content.add_widget(email_field)

        button = MDFlatButton(
            text="Send",
            theme_text_color="Custom",
            text_color=self.core.theme_cls.primary_color,
            on_release=lambda x: self.user_controller.reset_password(email=email_field.text),
        )

        self.core.show_dialog(button=button, content=content)

        self.core.dialog.title = 'Enter your Email'


class RegistrateScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(RegistrateScreen, self).__init__(**kwargs)
        self.user_controller = UserController(screen=self)

    def on_pre_leave(self, *args):
        for field_name in self.ids.keys():
            if 'field' in field_name:
                self.ids[field_name].text = ''

    def registrate(self, email, password, re_password):
        self.user_controller.registrate(email=email, password=password, re_password=re_password)


class ChangePasswordScreen(MDScreen):

    def __init__(self, **kwargs):
        super(ChangePasswordScreen, self).__init__(**kwargs)
        self.user_controller = UserController(screen=self)

    def on_pre_leave(self, *args):
        for field_name in self.ids.keys():
            if 'field' in field_name:
                self.ids[field_name].text = ''

    def change_password(self, current_password, new_password, re_new_password):
        self.user_controller.set_password(current_password=current_password, new_password=new_password, re_new_password=re_new_password)


class MainScreen(MDScreen):
    core = ObjectProperty()
    email = StringProperty('email')
    credit = NumericProperty()
    avatar = StringProperty('avatar')

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.user_controller = UserController(screen=self)

    def show_ads(self):
        if platform == 'android':
            self.core.ads.show_rewarded_ad()

    def open_settings(self):
        self.ids.nav_drawer.set_state("close")
        self.core.root.transition = MDSwapTransition()
        self.core.root.current = 'settings_screen'

    def open_collection(self):
        screen = self.core.root.current
        self.core.root.ids.collection_screen.ids.selection_list.back_item = ['arrow-left', lambda x: self.core.back(screen=screen)]
        self.ids.nav_drawer.set_state("close")
        self.core.root.transition = MDSwapTransition()
        self.core.root.current = 'collection_screen'

    def open_buy_credits(self):
        self.ids.nav_drawer.set_state('close')
        self.core.root.transition = MDSwapTransition()
        self.core.root.current = 'buy_credits_screen'

    def exit(self):
        self.ids.nav_drawer.set_state("close")
        self.user_controller.un_login()


class CreateImageScreen(MDScreen):
    core = ObjectProperty()
    prompt = StringProperty()
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')
    price = NumericProperty()

    def __init__(self, **kwargs):
        super(CreateImageScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.user_controller = UserController(screen=self)

    @property
    def check_enough_credit(self):
        self.price = self.image_count * settings.CREDIT_ONE_GENERATE
        if self.price <= self.user_controller.user.credit:
            return True
        else:
            return False

    def create(self):

        def callback(request, response):
            self.user_controller.update_user(field_name='credit', field_value=self.price, credit='minus')

            self.ids.create_spin.active = False

            if len(response['data']) == 1:
                url = response['data'][0].get('url')

                image = MyImage(
                    sm=self.parent,
                    source=url,
                    fit_mode='contain',
                    mipmap=True,
                )

                self.ids.image_section.add_widget(image)
            elif len(response['data']) > 1:
                swiper = MDSwiper(
                    size_hint_y=None,
                    pos_hint={'center_x': .5, 'center_y': .5},
                    height=self.ids.image_section.height,
                )

                for el in response['data']:
                    url = el.get('url')

                    item = MDSwiperItem()

                    image = MyImage(
                        sm=self.parent,
                        source=url,
                        mipmap=True,
                        fit_mode='contain',
                    )

                    item.add_widget(image)
                    swiper.add_widget(item)

                self.ids.image_section.add_widget(swiper)

        def output_error(error):
            self.ids.create_spin.active = False
            if type(error) is dict:
                if {'error'} & set(error):
                    self.core.show_dialog()
                    self.core.dialog.text = error.get('error')

            image = Image(
                source='assets/img/default.png',
                mipmap=True,
            )

            self.ids.image_section.add_widget(image)

        def callback_failure(request, response):
            output_error(error=response)

        def callback_error(request, error):
            output_error(error=error)

        if all([self.prompt, self.image_count, self.image_size]):

            if self.check_enough_credit:
                for widget in self.ids.image_section.children:
                    if isinstance(widget, MyImage) or isinstance(widget, MDSwiper) or isinstance(widget, Image):
                        self.ids.image_section.remove_widget(widget)

                self.ids.create_spin.active = True

                self.openai_controller.image_generation(
                    prompt=self.prompt,
                    image_count=self.image_count,
                    image_size=self.image_size,
                    callback=callback,
                    error=callback_error,
                    failure=callback_failure,
                )
            else:
                self.core.show_dialog()
                self.core.dialog.title = 'success!'
                self.core.dialog.text = 'You dont have enough credits'


class EditImageScreen(MDScreen):
    core = ObjectProperty()
    prompt = StringProperty()
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')
    image_original = io.BytesIO()
    image_mask = io.BytesIO()
    price = NumericProperty()

    def __init__(self, **kwargs):
        super(EditImageScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.user_controller = UserController(screen=self)

    @property
    def check_enough_credit(self):
        self.price = self.image_count * settings.CREDIT_ONE_GENERATE
        if self.price <= self.user_controller.user.credit:
            return True
        else:
            return False

    def add_image(self, path):
        self.ids.add_image_button.disabled = True

        for widget in self.ids.image_section.children:
            if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                self.ids.image_section.remove_widget(widget)

        image = MyImage(
            disabled=True,
            source=path,
            fit_mode='contain',
            mipmap=True,
        )

        self.ids.image_section.add_widget(image)
        if len(self.ids.edit_top_bar.right_action_items) == 0:
            self.ids.edit_top_bar.right_action_items.append(["autorenew", lambda x: self.reload_image()])
            self.ids.edit_top_bar.right_action_items.append(["broom", lambda x: self.clear_selection()])

        with PilImage.open(path) as img:
            new = img.resize(size=(256, 256))
            new.save(self.image_original, format='png')

    def edit_image(self):

        def callback(request, response):
            self.user_controller.update_user(field_name='credit', field_value=self.price, credit='minus')

            self.ids.edit_spin.active = False

            if len(response['data']) == 1:
                url = response['data'][0].get('url')

                image = MyImage(
                    sm=self.parent,
                    source=url,
                    fit_mode='contain',
                    mipmap=True,
                )

                self.ids.image_section.add_widget(image)
            elif len(response['data']) > 1:
                swiper = MDSwiper()

                for el in response['data']:
                    url = el.get('url')

                    item = MDSwiperItem()

                    image = MyImage(
                        sm=self.parent,
                        source=url,
                        mipmap=True,
                        fit_mode='contain',
                    )

                    item.add_widget(image)
                    swiper.add_widget(item)

                self.ids.image_section.add_widget(swiper)

        def output_error(error):
            self.ids.edit_spin.active = False
            self.ids.add_image_button.disabled = False

            self.ids.edit_top_bar.right_action_items = []

            if type(error) is dict:
                if {'error'} & set(error):
                    self.core.show_dialog()
                    self.core.dialog.text = error.get('error')

        def callback_failure(request, response):
            output_error(error=response)

        def callback_error(request, error):
            output_error(error=error)

        self.image_original.seek(0)
        if len(self.image_original.getvalue()) > 0:
            if all([self.prompt, self.image_count, self.image_size]):
                if self.check_enough_credit:
                    for widget in self.ids.image_section.children:
                        if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                            if isinstance(widget, MyImage) and widget.disabled:
                                mask_img = self.ids.image_section.children[0].get_mask_image()
                                mask_data = io.BytesIO()
                                mask_img.save(mask_data, flipped=True, fmt='png')

                                with PilImage.open(mask_data) as img:
                                    new = img.resize(size=(256, 256))
                                    new.save(self.image_mask, format='png')

                            self.ids.image_section.remove_widget(widget)

                    self.ids.add_image_button.disabled = True
                    self.ids.edit_spin.active = True

                    self.image_original.seek(0)
                    png_image_original = self.image_original.getvalue()
                    im_b64_image_original = base64.b64encode(png_image_original).decode('utf-8')

                    self.image_mask.seek(0)
                    png_image_mask = self.image_mask.getvalue()
                    im_b64_image_mask = base64.b64encode(png_image_mask).decode('utf-8')

                    self.openai_controller.image_edit(
                        image=im_b64_image_original,
                        mask=im_b64_image_mask,
                        prompt=self.prompt,
                        image_count=self.image_count,
                        image_size=self.image_size,
                        callback=callback,
                        on_error=callback_error,
                        on_failure=callback_failure,
                    )
                else:
                    self.core.show_dialog()
                    self.core.dialog.title = 'success!'
                    self.core.dialog.text = 'You dont have enough credits'

    def clear_selection(self):
        for widget in self.ids.image_section.children:
            if isinstance(widget, MyImage):
                widget.clear_selection()

    def reload_image(self):
        for widget in self.ids.image_section.children:
            if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                self.ids.image_section.remove_widget(widget)

        self.image_original.truncate(0)
        self.image_mask.truncate(0)
        self.ids.add_image_button.disabled = False

        while len(self.ids.edit_top_bar.right_action_items) !=0:
            self.ids.edit_top_bar.right_action_items.remove(self.ids.edit_top_bar.right_action_items[-1])


class VariableImageScreen(MDScreen):
    core = ObjectProperty()
    image = io.BytesIO()
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')
    price = NumericProperty()

    def __init__(self, **kwargs):
        super(VariableImageScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.user_controller = UserController(screen=self)

    @property
    def check_enough_credit(self):
        self.price = self.image_count * settings.CREDIT_ONE_GENERATE
        if self.price <= self.user_controller.user.credit:
            return True
        else:
            return False

    def add_image(self, path):
        self.ids.add_image_button.disabled = True

        for widget in self.ids.image_section.children:
            if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                self.ids.image_section.remove_widget(widget)

        image = MyImage(
            source=path,
            fit_mode='contain',
            mipmap=True,
        )

        self.ids.image_section.add_widget(image)
        if len(self.ids.variable_top_bar.right_action_items) == 0:
            self.ids.variable_top_bar.right_action_items.append(["autorenew", lambda x: self.reload_image()])

        with PilImage.open(path) as img:
            new = img.resize(size=(256, 256))
            new.save(self.image, format='png')

    def reload_image(self):
        for widget in self.ids.image_section.children:
            if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                self.ids.image_section.remove_widget(widget)

        self.image.truncate(0)
        self.ids.add_image_button.disabled = False

        self.ids.variable_top_bar.right_action_items.remove(self.ids.variable_top_bar.right_action_items[-1])

    def generate(self):

        def callback(request, response):
            self.user_controller.update_user(field_name='credit', field_value=self.price, credit='minus')

            self.ids.variable_spin.active = False

            if len(response['data']) == 1:
                url = response['data'][0].get('url')

                image = MyImage(
                    sm=self.parent,
                    source=url,
                    fit_mode='contain',
                    mipmap=True,
                )

                self.ids.image_section.add_widget(image)
            elif len(response['data']) > 1:
                swiper = MDSwiper()

                for el in response['data']:
                    url = el.get('url')

                    item = MDSwiperItem()

                    image = MyImage(
                        sm=self.parent,
                        source=url,
                        mipmap=True,
                        allow_stretch=True,
                    )

                    item.add_widget(image)
                    swiper.add_widget(item)

                self.ids.image_section.add_widget(swiper)

        def output_error(error):
            self.ids.variable_spin.active = False
            self.ids.add_image_button.disabled = False

            self.ids.variable_top_bar.right_action_items = []

            if type(error) is dict:
                if {'error'} & set(error):
                    self.core.show_dialog()
                    self.core.dialog.text = error.get('error')

        def callback_failure(request, response):
            output_error(error=response)

        def callback_error(request, error):
            output_error(error=error)

        self.image.seek(0)
        if len(self.image.getvalue()) > 0:
            if all([self.image_count, self.image_size]):
                if self.check_enough_credit:
                    for widget in self.ids.image_section.children:
                        if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                            self.ids.image_section.remove_widget(widget)

                    self.ids.add_image_button.disabled = True
                    self.ids.variable_spin.active = True

                    self.image.seek(0)
                    image_png = self.image.getvalue()
                    im_b64_image = base64.b64encode(image_png).decode('utf-8')

                    self.openai_controller.image_variation(
                        image=im_b64_image,
                        image_count=self.image_count,
                        image_size=self.image_size,
                        callback=callback,
                        on_error=callback_error,
                        on_failure=callback_failure,
                    )
                else:
                    self.core.show_dialog()
                    self.core.dialog.title = 'success!'
                    self.core.dialog.text = 'You dont have enough credits'


class ChatGptScreen(MDScreen):
    core = ObjectProperty()
    prompt = StringProperty()

    def __init__(self, **kwargs):
        super(ChatGptScreen, self).__init__(*kwargs)
        self.openai_controller = OpenAIController()

    def on_pre_enter(self, *args):
        Window.softinput_mode = 'pan'

    def on_pre_leave(self, *args):
        Window.softinput_mode = 'below_target'

    def send(self):

        def callback(request, response):
            text = response['choices'][0].get('message').get('content').lstrip()

            lab = Label(text=text, font_size=sp(16), padding=[dp(20), dp(5)])
            lab.texture_update()
            w, h = lab.texture_size

            if w > dp(300):
                lab = Label(text=text, font_size=sp(16), padding=[dp(20), dp(5)], text_size=(dp(300), None))
                lab.texture_update()
                w, h = lab.texture_size

            msg = {
                'width': w,
                'height': h,
                'text': text,
                'theme_text_color': 'Custom',
                'text_color': (1, 1, 1, 1),
                'font_style': 'Message',
                'bg_color': (.2, .2, .2, 1),
                'radius': [10, 10, 10, 10],
                'pos_hint': {'left': 1},
            }

            self.ids.chat_gpt.data.append(msg)

        if self.prompt:

            label = Label(text=self.prompt, font_size=sp(16), padding=[dp(20), dp(5)])
            label.texture_update()
            width, height = label.texture_size

            if width > dp(300):
                label = Label(text=self.prompt, font_size=sp(16), padding=[dp(20), dp(5)], text_size=(dp(300), None))
                label.texture_update()
                width, height = label.texture_size

            message = {
                'width': width,
                'height': height,
                'text': self.prompt,
                'theme_text_color': 'Custom',
                'text_color': (1, 1, 1, 1),
                'font_style': 'Message',
                'bg_color': 'blue',
                'radius': [10, 10, 10, 10],
                'pos_hint': {'right': 1},
            }

            self.ids.chat_gpt.data.append(message)

            msg = [{'role': 'user', 'content': self.prompt}]

            print(f"{self.num_tokens_from_messages(messages=msg)} prompt tokens counted.")

            # self.openai_controller.chat_completion(
            #     prompt=self.prompt,
            #     callback=callback,
            # )

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo"):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            print(f"""num_tokens_from_messages() is not presently implemented for model {model}.
      See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")


class CollectionScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(CollectionScreen, self).__init__(**kwargs)
        self.image_controller = ImageController(screen=self)

        menu_items = [
            {
                'text': 'Choose all',
                'viewclass': 'OneLineListItem',
                'on_release': lambda: (self.ids.selection_list.selected_all(), self.menu.dismiss()),
            }
        ]

        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=2.5,
        )

    def menu_callback(self, button):
        self.menu.caller = button
        self.menu.open()

    def delete_images(self, widget_list):
        images_id = [widget.children[1].img_id for widget in widget_list]

        def del_images():
            self.image_controller.del_images(images_id=images_id, widget_list=widget_list)
            self.core.dialog.dismiss()

        button = MDFlatButton(
            text="Delete",
            theme_text_color="Custom",
            text_color=self.core.theme_cls.primary_color,
            on_release=lambda x: del_images(),
        )

        self.core.show_dialog(button=button)
        self.core.dialog.title = 'Delete'
        self.core.dialog.text = 'Are you sure you want to delete?'


class OpenImageScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(OpenImageScreen, self).__init__(**kwargs)
        self.user_controller = UserController(screen=self)
        self.image_controller = ImageController(screen=self)

    def back(self, screen):
        if len(self.ids.app_bar.right_action_items) > 1:
            self.ids.app_bar.right_action_items.remove(self.ids.app_bar.right_action_items[0])
        self.parent.transition = FallOutTransition()
        self.parent.current = screen

    def download(self, img):

        def save_image():
            image = CoreImage(img.texture)

            if platform == 'android':
                private_path = join(self.core.ss.get_cache_dir(), f'{str(uuid.uuid4())}.png')

                image.save(private_path)

                if exists(private_path):
                    self.core.ss.copy_to_shared(private_path)

            if img.back_screen in ('create_image_screen', 'edit_image_screen', 'variable_image_screen'):
                data = io.BytesIO()
                image.save(data, fmt='png')
                png_bytes = data.read()
                im_b64 = base64.b64encode(png_bytes).decode('utf-8')

                data_image = {
                    'user': self.user_controller.user.id,
                    'source': im_b64,
                }

                for screen in self.core.root.screens:
                    if screen.name == img.back_screen and screen.name != 'variable_image_screen':
                        data_image['description'] = screen.prompt

                self.image_controller.save_image(data_image=data_image)

            self.core.dialog.dismiss()

        button = MDFlatButton(
            text="Save",
            theme_text_color="Custom",
            text_color=self.core.theme_cls.primary_color,
            on_release=lambda x: save_image(),
        )

        self.core.show_dialog(button=button)
        self.core.dialog.title = 'Save image'
        self.core.dialog.text = 'Do you want to save the picture?'

    def delete(self, img_id, widget):

        def del_image():
            self.image_controller.del_image(image_id=img_id, widget=widget)
            self.core.dialog.dismiss()

        button = MDFlatButton(
            text="Delete",
            theme_text_color="Custom",
            text_color=self.core.theme_cls.primary_color,
            on_release=lambda x: del_image(),
        )

        self.core.show_dialog(button=button)
        self.core.dialog.title = 'Delete'
        self.core.dialog.text = 'Are you sure you want to delete??'


class SettingsScreen(MDScreen):
    pass


class BuyCreditsScreen(MDScreen):
    LICENSE_KEY = settings.PLAY_CONSOLE_KEY

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

    def __init__(self, **kwargs):
        super(BuyCreditsScreen, self).__init__(**kwargs)
        if platform == 'android':
            self.bp = BillingProcessor(self.LICENSE_KEY, self.product_purchased, self.billing_error,
                                       onBillingInitializedMethod=self.billing_initialized)

    def on_pre_enter(self, *args):
        if platform == 'android':

            Logger.info(f"is_initialized: {self.bp.is_initialized()}")
            Logger.info(f"is_iab_service_available: {self.bp.is_iab_service_available()}")
            Logger.info(f"is_subscription_update_supported: {self.bp.is_subscription_update_supported()}")

            owned_products = self.bp.list_owned_products()
            owned_subscriptions = self.bp.list_owned_subscriptions()

            for product in owned_products:
                Logger.info(f"Product: {product}")

            for subscription in owned_subscriptions:
                Logger.info(f"Subscription: {subscription}")

    def open_payment_layout(self, sku):
        if self.bp.is_purchased(sku):
            toast("Already Purchased")
            pi = self.bp.get_purchase_info(sku)
            details = {
                "responseData": pi.responseData,
                "signature": pi.signature,
                "purchaseData": {
                    "orderId": pi.purchaseData.orderId,
                    "productId": pi.purchaseData.productId,
                    "purchaseTime": pi.purchaseData.purchaseTime,
                    "purchaseToken": pi.purchaseData.purchaseToken,
                    "purchaseState": pi.purchaseData.purchaseState,
                    "autoRenewing": pi.purchaseData.autoRenewing,
                }
            }
            Logger.info(f"get_purchase_info: {details}")
            self.bp.consume_purchase_async(sku)
            return
        elif self.bp.is_subscribed(sku):
            toast("Already Subscribed")
            pi = self.bp.get_subscription_purchase_info(sku)
            details = {
                "responseData": pi.responseData,
                "signature": pi.signature,
                "purchaseData": {
                    "orderId": pi.purchaseData.orderId,
                    "productId": pi.purchaseData.productId,
                    "purchaseTime": pi.purchaseData.purchaseTime,
                    "purchaseToken": pi.purchaseData.purchaseToken,
                    "purchaseState": pi.purchaseData.purchaseState,
                    "autoRenewing": pi.purchaseData.autoRenewing,
                }
            }
            Logger.info(f"get_subscription_purchase_info: {details}")
            return
        setattr(self, 'product_id', sku)
        self.ids.bottom_sheet.open()

    def initiate_purchase(self, method_name):

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
            toast("Payment method not implemented")

    def product_purchased(self, product_id, purchase_info):
        toast("Product purchased")
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
            toast("No purchase details received")


class SpeechToTextScreen(MDScreen):
    core = ObjectProperty()
    sound_path = StringProperty()
    sound = ObjectProperty()
    sound_pos = NumericProperty()

    def __init__(self, **kwargs):
        super(SpeechToTextScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()

    def sound_play(self):
        if self.sound:
            if self.sound.state == 'play':
                self.sound_pos = self.sound.get_pos()
                self.sound.stop()
                self.ids.sound_option.icon_play = 'play'
            elif self.sound.state == 'stop':
                if self.sound_pos:
                    self.sound.seek(self.sound_pos)
                self.sound.play()
                self.ids.sound_option.icon_play = 'pause'

    def sound_stop(self):
        if self.sound.state == 'play':
            self.ids.sound_option.icon_play = 'play'

        self.sound.stop()
        self.sound_pos = 0

    def delete_sound(self):
        if self.sound.state == 'play':
            self.sound.stop()

        if self.ids.audio_transcript.text:
            self.ids.audio_transcript.text = ''

        self.sound = False
        self.sound_path = ''
        self.sound_pos = 0
        self.ids.sound.icon = ''
        self.ids.sound.text = ''
        self.ids.sound_option.icon_play = ''
        self.ids.sound_option.icon_stop = ''
        self.ids.delete_button.icon = ''
        self.ids.add_sound_button.disabled = False

    def transcript(self):
        def callback(request, response):
            self.ids.speech_spin.active = False
            self.ids.audio_transcript.text = response['data']

        if self.sound_path:

            remove_widgets = []
            translate = False

            for widget in self.ids.speech_layout.children:
                if isinstance(widget, MDRaisedButton) or isinstance(widget, MDChip):
                    if isinstance(widget, MDChip):
                        translate = widget.active
                    remove_widgets.append(widget)

            self.ids.speech_layout.clear_widgets(remove_widgets)

            self.ids.speech_spin.active = True

            with open(self.sound_path, 'rb') as audio_file:
                base64_audio = base64.b64encode(audio_file.read()).decode('utf-8')
                name = audio_file.name.split('/')[-1]

                self.openai_controller.speech_to_text(
                    audio_file=base64_audio,
                    audio_name=name,
                    callback=callback,
                    translate=translate,
                )





