from kivy.properties import StringProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.core.clipboard import Clipboard
from kivy.utils import platform

if platform == 'android':
    from kivymd.toast import toast


class Message(RectangularRippleBehavior, ButtonBehavior, MDRelativeLayout):
    message = StringProperty()
    time = StringProperty()
    image_path = StringProperty()
    triangle_points = ListProperty()

    def on_release(self):
        Clipboard.copy(self.message)

        if platform == 'android':
            toast(
                text="Text message copied to clipboard",
                length_long=True,
                gravity=40,
                y=self.top,
                x=0,
            )