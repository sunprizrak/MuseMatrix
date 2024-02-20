from kivy.metrics import dp, sp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from controller.user import UserController
from .layout import BaseScreen


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
            error_text = ''
            if type(error) is str:
                error_text += error
            elif type(error) is dict:
                if {'current_password', 'new_password', 're_new_password'} & set(error):
                    for el in {'current_password', 'new_password', 're_new_password'} & set(error):
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
                    theme_font_size='Custom',
                    font_size=sp(13),
                ),
                padding=[0, dp(10), 0, 0],
                adaptive_height=True,
            )

            self.app.show_dialog(title='Oops!', content=content)

        def _on_success(request, response):
            title = 'success!'
            text = 'Password has been successfully changed!'

            content = MDBoxLayout(
                MDLabel(
                    text=text,
                ),
                padding=[0, dp(10), 0, 0],
            )

            self.app.show_dialog(title=title, content=content)

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