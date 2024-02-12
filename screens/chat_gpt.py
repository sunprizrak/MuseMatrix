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
from .layout import BaseScreen


class ChatGptScreen(BaseScreen):
    prompt = StringProperty()

    def __init__(self, **kwargs):
        super(ChatGptScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.user_controller = UserController()

    def on_pre_enter(self, *args):
        # if platform == 'android':
            # color_nav = self.theme_cls.primary_color
            # color_stat = self.theme_cls.primary_color
            # self.app.change_android_color(color_nav=color_nav, color_stat=color_stat)

        Window.softinput_mode = 'pan'

    def on_pre_leave(self, *args):
        # if platform == 'android':
        #     self.app.change_android_color()

        Window.softinput_mode = 'below_target'

    def __create_message(self, text, sense=None, spin=None):
        label = Label(text=text, font_size=sp(16), padding=[dp(15), dp(15), dp(35), dp(10)])
        label.texture_update()
        width, height = label.texture_size

        if platform == 'android':
            max_width = dp((Window.width * 0.3) / 100 * 80)
        else:
            max_width = dp(Window.width / 100 * 80)

        min_width = dp(60)

        if width > max_width:
            label = Label(text=text, font_size=sp(16), padding=dp(15), text_size=(max_width, None))
            label.texture_update()
            width, height = label.texture_size
        elif width < min_width:
            width = min_width

        def _calculate_triangle_points():
            triangle_height = dp(10)  # Высота треугольника
            triangle_base = dp(15)  # Основание треугольника

            triangle_x = width - triangle_base / 2
            triangle_y = 0

            if sense:
                triangle_x = 0 - triangle_base / 2

            points = [
                triangle_x, triangle_y,
                triangle_x + triangle_base, triangle_y,
                triangle_x + triangle_base / 2, triangle_y + triangle_height
            ]
            return points

        curr_time = time.strftime('%H:%M', time.localtime())

        triangle_points = _calculate_triangle_points()

        message = {
            'width': width,
            'height': height,
            'message': text,
            'time': curr_time if not spin else '',
            'triangle_points': triangle_points,
            'image_path': 'assets/gif/message_await.gif' if spin else 'assets/img/message_transparent.png',
            'radius': [dp(15), dp(15), dp(15), 0] if sense else [dp(15), dp(15), 0, dp(15)],
            'theme_bg_color': 'Custom',
            'md_bg_color': '#2979FF' if sense else self.app.theme_cls.backgroundColor,
            'pos_hint': {'left': 1} if sense else {'right': 1},
        }

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
            self.ids.chat_gpt.data.pop(-1)
            self.ids.send_button.disabled = False

            if 'message' in response:
                text = response.get('message')  # .lstrip()
                self.user_controller.user.chat_token = response.get('chat_token')
                self.app.root.ids.main_screen.chat_token = self.user_controller.user.chat_token

                response_message = self.__create_message(text=text, sense=True)

                self.ids.chat_gpt.data.append(response_message)
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
            self.ids.chat_gpt.data.append(send_message)

            await_message = self.__create_message(text=' ', sense=True, spin=True)
            self.ids.chat_gpt.data.append(await_message)

            self.ids.send_button.disabled = True

            self.openai_controller.chat_completion(
                prompt=self.prompt,
                on_success=_on_success,
                on_error=_on_error,
                on_failure=_on_failure,
            )