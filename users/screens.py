from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

from .controller import UserController


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
        #self.core.dialog.content_cls.add_widget(email_field)


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



