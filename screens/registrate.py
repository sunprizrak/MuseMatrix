from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from controller.user import UserController
from .layout import BaseScreen
from kivy.utils import platform

if platform == 'android':
    from kivymd.toast import toast


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
            error_text = ''
            if type(error) is str:
                error_text = error
            elif type(error) is dict:
                if {'email', 'password', 're_password'} & set(error):
                    for el in {'email', 'password', 're_password'} & set(error):
                        if el == 'email' and 'email address already exists' in error.get(el)[0]:
                            def _callback(instance, param):
                                def _on_callback(request, response):
                                    if platform == 'android':
                                        toast("email sent to mail")

                                self.user_controller.resend_activation(email=self.ids.email_field.text, on_success=_on_callback)
                                self.app.close_dialog(self)

                            helper_text = ' '.join(error.get(el)[0].split(' ')[2:])
                            error_text = "[ref=Resend activation email][color=0000ff]Resend activation email[/color][/ref]"

                            field = self.ids.get(f'{el}_field')
                            field.error = True

                            content = MDBoxLayout(
                                MDLabel(
                                    text=error_text,
                                    markup=True,
                                    padding=[0, dp(10), 0, 0],
                                    on_ref_press=_callback,
                                ),
                            )
                            return self.app.show_dialog(title='Notice!', sup_text=helper_text, content=content)
                        else:
                            error_text = f'{el}: {error.get(el)[0]}'
                            field = self.ids.get(f'{el}_field')
                            field.error = True
                elif {'non_field_errors'} & set(error):
                    error_text = error.get('non_field_errors')[0]
                    for el in self.ids:
                        if 'password' in el:
                            field = self.ids.get(f'{el}')
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
            self.app.root.current = 'login_screen'

            title = 'success!'
            text = f'Activation email has been sent to your email {email}, confirm your email to continue'

            content = MDBoxLayout(
                MDLabel(
                    text=text,
                    padding=[0, dp(10), 0, 0],
                ),
            )

            self.app.show_dialog(title=title, content=content)

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