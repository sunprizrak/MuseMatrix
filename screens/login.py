from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

from controller.user import UserController
from .layout import BaseScreen


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
            error_text = ''
            if type(error) is str:
                error_text += error
            elif type(error) is dict:
                if len({'password', 'email'} & set(error)) > 0:
                    for el in {'password', 'email'} & set(error):
                        text = error.get(el)[0]
                        error_text += f'{el}: {text}\n'
                        field = self.ids.get(f'{el}_field')
                        field.error = True
                else:
                    for value in error.values():
                        error_text += f'{value[0]}\n'

            content = MDBoxLayout(
                MDLabel(
                    text=error_text,
                    padding=[0, dp(10), 0, 0],
                ),
            )

            self.app.show_dialog(title='Oops!', content=content)

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
            MDTextFieldHintText(
                text='Email',
                theme_text_color='Custom',
                text_color_normal='white',
                theme_font_name="Custom",
                font_name='Hacked',
            ),
            mode='outlined',
            theme_text_color='Custom',
            text_color_normal='white',
        )

        content.add_widget(email_field)

        button = MDButton(
            MDButtonText(
                text='Send',
                theme_text_color="Custom",
                text_color='white',
                theme_font_name="Custom",
                font_name='Hacked',
            ),
            style='filled',
            theme_bg_color='Custom',
            md_bg_color='green',
            on_release=lambda x: self.user_controller.reset_password(email_field.text),
        )

        self.app.show_dialog(
            title='Enter your Email',
            sup_text='A recovery link will be sent to your email',
            button=button,
            content=content,
        )
