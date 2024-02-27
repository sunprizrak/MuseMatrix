import time
from kivy.core.window import Window
from kivy.metrics import sp, dp
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.utils import platform
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from controller.openai import OpenAIController
from controller.user import UserController
from widgets.Message import Message
from .layout import BaseScreen


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

    def __create_message(self, text, sense=None, spin=None):
        curr_time = time.strftime('%H:%M', time.localtime())

        message = Message(
            message=text,
            time=curr_time if not spin else '',
            image_path='assets/gif/message_await.gif' if spin else 'assets/img/message_transparent.png',
            radius=[dp(15), dp(15), dp(15), 0] if sense else [dp(15), dp(15), 0, dp(15)],
            theme_bg_color='Custom',
            md_bg_color='#2979FF' if sense else self.app.theme_cls.backgroundColor,
            pos_hint={'left': 1} if sense else {'right': 1},
        )

        return message

    def send(self):
        def _output_error(error):
            self.ids.chat_gpt.data.pop(-1)
            self.ids.send_button.disabled = False
            print(error)

        def _on_error(request, error):
            _output_error(error)

        def _on_failure(request, response):
            _output_error(response)

        def _on_success(request, response):
            widget = self.ids.chat_gpt_box.children[0]
            self.ids.chat_gpt_box.remove_widget(widget)
            self.ids.send_button.disabled = False

            if 'message' in response:
                text = response.get('message')
                self.user_controller.user.chat_token = response.get('chat_token')
                self.app.root.ids.main_screen.chat_token = self.user_controller.user.chat_token

                response_message = self.__create_message(text=text, sense=True)

                self.ids.chat_gpt_box.add_widget(response_message)
            elif 'notice' in response:
                text = response.get('notice')

                content = MDBoxLayout(
                    MDLabel(
                        text=text,
                    ),
                    padding=[0, dp(10), 0, dp(10)],
                )

                self.app.show_dialog(
                    title='Oops!',
                    content=content,
                )

        if self.prompt:

            send_message = self.__create_message(text=self.prompt)
            self.ids.chat_gpt_box.add_widget(send_message)

            await_message = self.__create_message(text=' ', sense=True, spin=True)
            self.ids.chat_gpt_box.add_widget(await_message)

            self.ids.send_button.disabled = True

            self.openai_controller.chat_completion(
                prompt=self.prompt,
                on_success=_on_success,
                on_error=_on_error,
                on_failure=_on_failure,
            )