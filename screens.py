from kivy import Logger
from kivy.core.window import Window
from kivy.metrics import sp, dp
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import FallOutTransition
from kivy.properties import StringProperty, ObjectProperty, BoundedNumericProperty, NumericProperty
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.swiper import MDSwiperItem, MDSwiper
from kivy.core.image import Image as CoreImage
from kivymd.uix.textfield import MDTextField
from kivymd.uix.transition import MDSwapTransition
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
from kivy.clock import Clock

logging.getLogger('PIL').setLevel(logging.WARNING)

if platform == 'android':
    from iabwrapper import BillingProcessor


class BaseScreen(MDScreen):
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.md_bg_color = self.app.theme_cls.bg_light


class ImageScreen(BaseScreen):
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')
    price = NumericProperty()

    def __init__(self, **kwargs):
        super(ImageScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.user_controller = UserController()

    def on_pre_enter(self, *args):
        if platform == 'android':
            color_nav = self.theme_cls.primary_color
            self.app.change_android_color(color_nav=color_nav)

    def on_pre_leave(self, *args):
        if platform == 'android':
            self.app.change_android_color()


class StartScreen(BaseScreen):
    pass


class LoginScreen(BaseScreen):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.user_controller = UserController()

    def on_pre_leave(self, *args):
        for field_name in self.ids.keys():
            if 'field' in field_name:
                self.ids[field_name].text = ''

    def login(self, email, password):

        def _output_error(error):
            if type(error) is str:
                self.app.show_dialog()
                self.app.dialog.text = error
            elif type(error) is dict:
                if len({'password', 'email'} & set(error)) > 0:
                    for el in {'password', 'email'} & set(error):
                        error_text = error.get(el)[0]
                        field = self.ids.get(f'{el}_field')
                        field.error = True
                        field.helper_text = error_text
                else:
                    error_text = ''
                    for value in error.values():
                        error_text += f'{value[0]}\n'
                    self.app.show_dialog()
                    self.app.dialog.text = error_text

        def _on_success(request, response):
            self.app.storage.put('auth_token', token=response.get('auth_token'))
            self.user_controller.authorized()

        def _on_error(request, error):
            _output_error(error)

        def _on_failure(request, response):
            _output_error(response)

        self.user_controller.auth(
            email=email,
            password=password,
            on_success=_on_success,
            on_error=_on_error,
            on_failure=_on_failure
        )

    def forgot_password(self):

        content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height="50dp",
        )

        email_field = MDTextField(
            hint_text='Email',
            mode='rectangle',
            text_color_normal='white',
            hint_text_color_normal='white',
        )

        content.add_widget(email_field)

        button = MDFlatButton(
            text="Send",
            theme_text_color="Custom",
            text_color=self.app.theme_cls.primary_color,
            on_release=lambda x: self.user_controller.reset_password(email_field.text),
        )

        self.app.show_dialog(button=button, content=content)

        self.app.dialog.title = 'Enter your Email'


class RegistrateScreen(BaseScreen):

    def __init__(self, **kwargs):
        super(RegistrateScreen, self).__init__(**kwargs)
        self.user_controller = UserController()

    def on_pre_leave(self, *args):
        for field_name in self.ids.keys():
            if 'field' in field_name:
                self.ids[field_name].text = ''

    def registrate(self, email, password, re_password):
        def _output_error(error):
            if type(error) is str:
                self.app.show_dialog()
                self.app.dialog.text = error
            elif type(error) is dict:
                if {'email', 'password', 're_password'} & set(error):
                    for el in {'email', 'password', 're_password'} & set(error):
                        if el == 'email' and 'email address already exists' in error.get(el)[0]:
                            def _callback():
                                def _on_callback(request, response):
                                    toast(f"email sent to mail")

                                self.user_controller.resend_activation(email=self.ids.email_field.text, on_success=_on_callback)
                                self.app.close_dialog(self)

                            self.app.show_dialog()
                            error_text = ' '.join(error.get(el)[0].split(' ')[2:])
                            self.app.dialog.text = f"{error_text}\n[ref=Resend activation email][color=0000ff]Resend activation email[/color][/ref]"
                            self.app.dialog.children[0].children[3].on_ref_press = lambda x: _callback()

                            field = self.ids.get(f'{el}_field')
                            field.error = True
                            field.helper_text = error_text
                        else:
                            error_text = error.get(el)[0]
                            field = self.ids.get(f'{el}_field')
                            field.error = True
                            field.helper_text = error_text
                elif {'non_field_errors'} & set(error):
                    error_text = error.get('non_field_errors')[0]
                    for el in self.ids:
                        if 'password' in el:
                            field = self.ids.get(f'{el}')
                            field.error = True
                            field.helper_text = error_text
                else:
                    error_text = ''
                    for value in error.values():
                        error_text += f'{value[0]}\n'
                    self.app.show_dialog()
                    self.app.dialog.text = error_text

        def _on_success(request, response):
            self.app.root.current = 'login_screen'
            self.app.show_dialog()
            self.app.dialog.title = 'success!'
            self.app.dialog.text = 'An email has been sent to you with an activation letter for your account, confirm it and login with email and password.'

        def _on_error(request, error):
            _output_error(error)

        def _on_failure(request, response):
            _output_error(response)

        self.user_controller.registrate(
            email=email,
            password=password,
            re_password=re_password,
            on_success=_on_success,
            on_error=_on_error,
            on_failure=_on_failure
        )


class ChangePasswordScreen(BaseScreen):

    def __init__(self, **kwargs):
        super(ChangePasswordScreen, self).__init__(**kwargs)
        self.user_controller = UserController()

    def on_pre_leave(self, *args):
        for field_name in self.ids.keys():
            if 'field' in field_name:
                self.ids[field_name].text = ''

    def change_password(self, current_password, new_password, re_new_password):
        def _output_error(error):
            if type(error) is str:
                self.app.show_dialog()
                self.app.dialog.text = error
            elif type(error) is dict:
                if {'current_password', 'new_password', 're_new_password'} & set(error):
                    for el in {'current_password', 'new_password', 're_new_password'} & set(error):
                        error_text = error.get(el)[0]
                        field = self.ids.get(f'{el}_field')
                        field.error = True
                        field.helper_text = error_text
                elif {'non_field_errors'} & set(error):
                    error_text = error.get('non_field_errors')[0]
                    for el in self.ids:
                        if 'new_password' in el:
                            field = self.ids.get(f'{el}')
                            field.error = True
                            field.helper_text = error_text
                else:
                    error_text = ''
                    for value in error.values():
                        error_text += f'{value[0]}\n'
                    self.app.show_dialog()
                    self.app.dialog.text = error_text

        def _on_success(request, response):
            self.app.show_dialog()
            self.app.dialog.title = 'success!'
            self.app.dialog.text = 'Password has been successfully changed!'

        def _on_error(request, error):
            _output_error(error)

        def _on_failure(request, response):
            _output_error(response)

        self.user_controller.set_password(
            current_password=current_password,
            new_password=new_password,
            re_new_password=re_new_password,
            on_success=_on_success,
            on_error=_on_error,
            on_failure=_on_failure
        )


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
        screen = self.app.root.current
        self.app.root.ids.collection_screen.ids.selection_list.back_item = ['arrow-left-bold', lambda x: self.app.back(screen)]
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


class CreateImageScreen(ImageScreen):
    prompt = StringProperty()

    def generate(self):

        def _on_success(request, response):
            self.ids.create_spin.active = False

            if 'data' in response:
                self.user_controller.user.coin = response.get('coin')
                self.app.root.ids.main_screen.coin = self.user_controller.user.coin

                if len(response['data']) == 1:
                    url = response['data'][0].get('url')

                    image = MyImage(
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

                    for index, el in enumerate(response['data']):
                        url = el.get('url')

                        item = MDSwiperItem()

                        image = MyImage(
                            source=url,
                            mipmap=True,
                            fit_mode='contain',
                            index=index,
                        )

                        item.add_widget(image)
                        swiper.add_widget(item)

                    self.ids.image_section.add_widget(swiper)
            elif 'notice' in response:
                image = Image(
                    source='assets/img/default.png',
                    mipmap=True,
                )

                self.ids.image_section.add_widget(image)

                self.app.show_dialog()
                self.app.dialog.title = 'Notice!'
                self.app.dialog.text = response['notice']

        def _output_error(error):
            self.ids.create_spin.active = False
            if type(error) is dict:
                if {'error'} & set(error):
                    self.app.show_dialog()
                    self.app.dialog.text = error.get('error')

            image = Image(
                source='assets/img/default.png',
                mipmap=True,
            )

            self.ids.image_section.add_widget(image)

        def _on_failure(request, response):
            _output_error(response)

        def _on_error(request, error):
            _output_error(error)

        if all([self.prompt, self.image_count, self.image_size]):
            for widget in self.ids.image_section.children:
                if isinstance(widget, MyImage) or isinstance(widget, MDSwiper) or isinstance(widget, Image):
                    self.ids.image_section.remove_widget(widget)

            self.ids.create_spin.active = True

            self.openai_controller.image_generation(
                prompt=self.prompt,
                image_count=self.image_count,
                image_size=self.image_size,
                on_success=_on_success,
                on_error=_on_error,
                on_failure=_on_failure,
            )


class EditImageScreen(ImageScreen):
    prompt = StringProperty()
    image_original = io.BytesIO()
    image_mask = io.BytesIO()

    def add_image(self, path):
        self.ids.add_image_button.disabled = True
        self.ids.add_image_button.opacity = 0

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

        def _on_success(request, response):
            self.ids.edit_spin.active = False

            if 'data' in response:
                self.user_controller.user.coin = response['coin']
                self.app.root.ids.main_screen.coin = self.user_controller.user.coin

                if len(response['data']) == 1:
                    url = response['data'][0].get('url')

                    image = MyImage(
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
                            source=url,
                            mipmap=True,
                            fit_mode='contain',
                        )

                        item.add_widget(image)
                        swiper.add_widget(item)

                    self.ids.image_section.add_widget(swiper)
            elif 'notice' in response:
                self.ids.add_image_button.disabled = False
                self.ids.edit_top_bar.right_action_items = []

                self.app.show_dialog()
                self.app.dialog.title = 'Notice!'
                self.app.dialog.text = response['notice']

        def _output_error(error):
            self.ids.edit_spin.active = False
            self.ids.add_image_button.disabled = False

            self.ids.edit_top_bar.right_action_items = []

            if type(error) is dict:
                if {'error'} & set(error):
                    self.app.show_dialog()
                    self.app.dialog.text = error.get('error')

        def _on_error(request, error):
            _output_error(error)

        def _on_failure(request, response):
            _output_error(response)

        self.image_original.seek(0)
        if len(self.image_original.getvalue()) > 0:
            if all([self.prompt, self.image_count, self.image_size]):
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
                    on_success=_on_success,
                    on_error=_on_error,
                    on_failure=_on_failure,
                )

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
        self.ids.add_image_button.opacity = 1

        while len(self.ids.edit_top_bar.right_action_items) != 0:
            self.ids.edit_top_bar.right_action_items.remove(self.ids.edit_top_bar.right_action_items[-1])


class VariableImageScreen(ImageScreen):
    image = io.BytesIO()

    def add_image(self, path):
        self.ids.add_image_button.disabled = True
        self.ids.add_image_button.opacity = 0

        for widget in self.ids.image_section.children:
            if isinstance(widget, Image) or isinstance(widget, MDSwiper):
                self.ids.image_section.remove_widget(widget)

        image = Image(
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
            if isinstance(widget, Image) or isinstance(widget, MDSwiper) or isinstance(widget, MyImage):
                self.ids.image_section.remove_widget(widget)

        self.image.truncate(0)
        self.ids.add_image_button.disabled = False
        self.ids.add_image_button.opacity = 1

        self.ids.variable_top_bar.right_action_items.remove(self.ids.variable_top_bar.right_action_items[-1])

    def generate(self):

        def _on_success(request, response):
            self.ids.variable_spin.active = False

            if 'data' in response:
                self.user_controller.user.coin = response['coin']
                self.app.root.ids.main_screen.coin = self.user_controller.user.coin

                if len(response['data']) == 1:
                    url = response['data'][0].get('url')

                    image = MyImage(
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
                            source=url,
                            mipmap=True,
                            fit_mode='contain',
                        )

                        item.add_widget(image)
                        swiper.add_widget(item)

                    self.ids.image_section.add_widget(swiper)
            elif 'notice' in response:
                self.ids.add_image_button.disabled = False

                self.ids.variable_top_bar.right_action_items = []

                self.app.show_dialog()
                self.app.dialog.title = 'Notice!'
                self.app.dialog.text = response['notice']

        def _output_error(error):
            self.ids.variable_spin.active = False
            self.ids.add_image_button.disabled = False

            self.ids.variable_top_bar.right_action_items = []

            if type(error) is dict:
                if {'error'} & set(error):
                    self.app.show_dialog()
                    self.app.dialog.text = error.get('error')

        def _on_error(request, error):
            _output_error(error)

        def _on_failure(request, response):
            _output_error(response)

        self.image.seek(0)
        if len(self.image.getvalue()) > 0:
            if all([self.image_count, self.image_size]):
                for widget in self.ids.image_section.children:
                    if isinstance(widget, MyImage) or isinstance(widget, MDSwiper) or isinstance(widget, Image):
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
                    on_success=_on_success,
                    on_error=_on_error,
                    on_failure=_on_failure,
                )


class ChatGptScreen(BaseScreen):
    prompt = StringProperty()

    def __init__(self, **kwargs):
        super(ChatGptScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.user_controller = UserController()

    def on_pre_enter(self, *args):
        Window.softinput_mode = 'pan'

    def on_pre_leave(self, *args):
        Window.softinput_mode = 'below_target'

    def send(self):

        def _on_success(request, response):
            if 'choices' in response:
                text = response['choices'][0].get('message').get('content').lstrip()
                self.user_controller.user.chat_token = response['chat_token']
                self.app.root.ids.main_screen.chat_token = self.user_controller.user.chat_token

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
            elif 'notice' in response:
                self.app.show_dialog()
                self.app.dialog.title = 'Notice!'
                self.app.dialog.text = response['notice']

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
                'bg_color': self.app.theme_cls.primary_color,
                'radius': [10, 10, 10, 10],
                'pos_hint': {'right': 1},
            }

            self.ids.chat_gpt.data.append(message)

            self.openai_controller.chat_completion(
                prompt=self.prompt,
                on_success=_on_success,
            )


class CollectionScreen(BaseScreen):

    def __init__(self, **kwargs):
        super(CollectionScreen, self).__init__(**kwargs)
        self.image_controller = ImageController()

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
            self.app.dialog.dismiss()

        button = MDFillRoundFlatButton(
            text="Delete",
            on_release=lambda x: del_images(),
        )

        self.app.show_dialog(button=button)
        self.app.dialog.title = 'Delete'
        self.app.dialog.text = 'Are you sure you want to delete?'


class OpenImageScreen(BaseScreen):
    back_screen = StringProperty()

    def __init__(self, **kwargs):
        super(OpenImageScreen, self).__init__(**kwargs)
        self.user_controller = UserController()
        self.image_controller = ImageController()

    def on_pre_enter(self, *args):
        screen = self.app.root.get_screen(self.back_screen)

        if self.back_screen == 'collection_screen':
            images = [el.instance_item for el in screen.ids.selection_list.children]
        else:
            for widget in screen.ids.image_section.children:
                if isinstance(widget, MyImage):
                    images = [widget]
                elif isinstance(widget, MDSwiper):
                    images = [el.children[0].children[0] for el in widget.children[0].children]

        images.reverse()

        for obj in images:

            image = Image(
                mipmap=True,
                texture=obj.texture,
                fit_mode='contain',
                pos_hint={'center_y': .5}
            )

            if self.back_screen == 'collection_screen':
                image.img_id = obj.img_id
                image.pre_parent = obj.parent

            self.ids.carousel.add_widget(image)

    def on_leave(self, *args):
        self.ids.carousel.clear_widgets()

    def back(self, screen):
        if len(self.ids.app_bar.right_action_items) > 1:
            self.ids.app_bar.right_action_items.remove(self.ids.app_bar.right_action_items[0])
        self.app.root.transition = FallOutTransition()
        self.app.root.current = screen

    def download(self, img):

        def save_image():
            image = CoreImage(img.texture)

            if platform == 'android':
                private_path = join(self.app.ss.get_cache_dir(), f'{str(uuid.uuid4())}.png')

                image.save(private_path)

                if exists(private_path):
                    self.app.ss.copy_to_shared(private_path)

            if self.back_screen in ('create_image_screen', 'edit_image_screen', 'variable_image_screen'):
                data = io.BytesIO()
                image.save(data, fmt='png')
                png_bytes = data.read()
                im_b64 = base64.b64encode(png_bytes).decode('utf-8')

                data_image = {
                    'user': self.user_controller.user.id,
                    'source': im_b64,
                }

                screen = self.app.root.get_screen(self.back_screen)

                if screen.name != 'variable_image_screen':
                    data_image['description'] = screen.prompt

                self.image_controller.save_image(data_image=data_image)

            self.app.dialog.dismiss()

        button = MDFillRoundFlatButton(
            text="Save",
            on_release=lambda x: save_image(),
        )

        self.app.show_dialog(button=button)
        self.app.dialog.title = 'Save image'
        self.app.dialog.text = 'Do you want to save the picture?'

    def delete(self, img_id, widget_selection):

        def del_image():
            self.image_controller.del_image(image_id=img_id, widget_selection=widget_selection, widget_carousel=self.ids.carousel.current_slide)
            self.app.dialog.dismiss()

        button = MDFillRoundFlatButton(
            text="Delete",
            on_release=lambda x: del_image(),
        )

        self.app.show_dialog(button=button)
        self.app.dialog.title = 'Delete'
        self.app.dialog.text = 'Are you sure you want to delete??'


class SettingsScreen(BaseScreen):
    pass


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
        if self.bp.is_subscribed(sku):
            toast("Already Subscribed")
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
            toast("No purchase details received")


class SpeechToTextScreen(BaseScreen):
    sound = ObjectProperty(allownone=True)
    sound_pos = NumericProperty()

    def __init__(self, **kwargs):
        super(SpeechToTextScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.user_controller = UserController()
        self.event = None

    def sound_play(self):
        if self.sound:
            if self.sound.state == 'play':
                self.sound_pos = self.sound.get_pos()
                self.sound.stop()
                self.ids.sound_option.icon_play = 'play'
                self.event.cancel()
            elif self.sound.state == 'stop':
                if self.sound_pos:
                    self.sound.seek(self.sound_pos)
                self.sound.play()
                self.ids.sound_option.icon_play = 'pause'

                end_sound = self.sound.length - self.sound.get_pos() + 1

                def _callback(args, **kwargs):
                    self.ids.sound_option.icon_play = 'play'

                self.event = Clock.schedule_once(callback=_callback, timeout=end_sound)
                self.event()

    def sound_stop(self):
        if self.sound.state == 'play':
            self.ids.sound_option.icon_play = 'play'

        self.sound.stop()
        self.sound_pos = 0

        if self.event:
            self.event.cancel()

    def delete_sound(self):
        if self.sound.state == 'play':
            self.sound.stop()

        if self.ids.audio_transcript.text:
            self.ids.audio_transcript.text = ''

        if self.ids.speech_spin.active is True:
            self.ids.speech_spin.active = False

        self.sound = None
        self.sound_pos = 0
        self.ids.sound.text = ''

        if self.event:
            self.event.cancel()

        remove_widgets = []

        for widget in self.ids.speech_layout.children:
            if isinstance(widget, MDRaisedButton) or isinstance(widget, MDChip):
                remove_widgets.append(widget)

        self.ids.speech_layout.clear_widgets(remove_widgets)

    def transcript(self):
        def _on_success(request, response):
            self.ids.audio_transcript.text = response['text']
            self.user_controller.user.coin = response['coin']
            self.app.root.ids.main_screen.coin = self.user_controller.user.coin

        def _on_error(request, error):
            print('error')
            _output_error(error)

        def _on_failure(request, response):
            print('failure')
            _output_error(response)

        def _output_error(error):
            print(error)
            button = MDRaisedButton(
                text='transcript',
                pos_hint={'center_x': .5, 'center_y': .5},
                font_size=sp(25),
                md_bg_color=self.theme_cls.primary_color,
                on_release=lambda x: self.transcript()
            )

            text_button = MDChipText(text='translate to english')

            chip = MDChip(
                pos_hint={'center_x': .5, 'center_y': .6},
                md_bg_color='grey',
                line_color="black",
                type='filter',
                selected_color='green',
            )

            chip.add_widget(text_button)

            self.ids.speech_layout.add_widget(button)
            self.ids.speech_layout.add_widget(chip)

        def _on_finish(request):
            self.ids.speech_spin.active = False

        if self.sound:

            remove_widgets = []
            translate = False

            for widget in self.ids.speech_layout.children:
                if isinstance(widget, MDRaisedButton) or isinstance(widget, MDChip):
                    if isinstance(widget, MDChip):
                        translate = widget.active
                    remove_widgets.append(widget)

            self.ids.speech_layout.clear_widgets(remove_widgets)

            self.ids.speech_spin.active = True

            length = int(self.sound.length / 60)

            with open(self.sound.source, 'rb') as audio_file:
                base64_audio = base64.b64encode(audio_file.read()).decode('utf-8')
                name = audio_file.name.split('/')[-1]

                self.openai_controller.speech_to_text(
                    audio_file=base64_audio,
                    audio_name=name,
                    audio_length=length,
                    on_failure=_on_failure,
                    on_error=_on_error,
                    on_finish=_on_finish,
                    on_success=_on_success,
                    translate=translate,
                )


class InstructionScreen(BaseScreen):

    def on_pre_enter(self, *args):
        if platform == 'android':
            color_nav = self.theme_cls.primary_color
            self.app.change_android_color(color_nav=color_nav)

    def on_pre_leave(self, *args):
        if platform == 'android':
            self.app.change_android_color()

    def move_to_screen(self, instance, value):
        if value == 'Purchase via google play store':
            self.app.root.transition = MDSwapTransition()
            self.app.root.current = 'buy_coins_screen'
        elif value == 'View ads':
            self.app.root.ids.main_screen.show_ads()