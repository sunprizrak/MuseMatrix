from kivy.core.window import Window
from kivy.graphics import Color, Triangle
from kivy.metrics import dp, sp
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.core.clipboard import Clipboard
from kivy.utils import platform

if platform == 'android':
    from kivymd.toast import toast


class MyChatLayout(MDBoxLayout):

    def __init__(self, **kwargs):
        super(MyChatLayout, self).__init__(**kwargs)

    def add_widget(self, widget, *args, **kwargs):
        message_line = MDRelativeLayout(
            size_hint_y=None,
        )

        message_line.add_widget(widget)
        widget = message_line
        return super(MyChatLayout, self).add_widget(widget, *args, **kwargs)


class Message(RectangularRippleBehavior, ButtonBehavior, MDRelativeLayout):
    message = StringProperty()
    time = StringProperty()
    image_path = StringProperty()
    text_widget = ObjectProperty()
    time_widget = ObjectProperty()

    def __init__(self, **kwargs):
        super(Message, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.text_widget = MDLabel(
            text=self.message,
            font_size=sp(16),
            padding=[dp(15), dp(10), dp(50), dp(15)],
            adaptive_size=True,
            pos_hint={'top': 1},
            halign='left',
        )
        self.add_widget(self.text_widget)

        self.time_widget = MDLabel(
            text=self.time,
            theme_font_size='Custom',
            font_size=sp(10),
            padding=[0, 0, dp(10), dp(5)],
            adaptive_size=True,
            bold=True,
            pos_hint={'right': 1}
        )
        self.add_widget(self.time_widget)

        image = Image(
            source=self.image_path,
            fit_mode='cover',
            anim_delay=0,
            mipmap=True,
        )
        self.add_widget(image)

    def on_parent(self, widget, parent):
        if parent is not None:
            self.text_widget.texture_update()
            self.time_widget.texture_update()

            width, height = self.text_widget.texture_size

            if platform == 'android':
                max_width = dp((Window.width * 0.3) / 100 * 80)
            else:
                max_width = dp(Window.width / 100 * 80)

            min_width = dp(60)

            if width > max_width:
                self.text_widget.padding = [dp(15), dp(10), dp(15), dp(15)]
                self.text_widget.adaptive_size = False
                self.text_widget.text_size = (max_width, None)
                self.text_widget.texture_update()
                width, height = self.text_widget.texture_size
            elif width < min_width:
                width = min_width

            self.size = (width, height)
            self.parent.size = self.size

            with self.canvas.before:
                Color(rgba=self.md_bg_color)
                triangle_points = self._calculate_triangle_points(width)
                Triangle(points=triangle_points)

    def _calculate_triangle_points(self, width):
        triangle_height = dp(10)  # Высота треугольника
        triangle_base = dp(15)  # Основание треугольника

        triangle_x = width - triangle_base / 2
        triangle_y = 0

        if 'left' in str(self.pos_hint):
            triangle_x = 0 - triangle_base / 2

        points = [
            triangle_x, triangle_y,
            triangle_x + triangle_base, triangle_y,
            triangle_x + triangle_base / 2, triangle_y + triangle_height
        ]

        return points

    def on_release(self):
        Clipboard.copy(self.message)

        if platform == 'android':
            toast(
                text="Text message copied to clipboard",
                length_long=True,
                gravity=40,
                y=self.top,
            )