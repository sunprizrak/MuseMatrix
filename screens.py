import time
from kivy import Logger
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import sp, dp
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import FallOutTransition
from kivy.properties import StringProperty, ObjectProperty, BoundedNumericProperty, NumericProperty
from kivymd.app import MDApp
from kivymd.uix.appbar import MDTopAppBar, MDTopAppBarLeadingButtonContainer, MDActionTopAppBarButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.swiper import MDSwiperItem, MDSwiper
from kivy.core.image import Image as CoreImage
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.transition import MDSwapTransition
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
from kivy.uix.carousel import Carousel



if platform == 'android':
    from iabwrapper import BillingProcessor
    from kivymd.toast import toast



#
#
#

#
#
#
#
#

#
#

#
#

#
#

#
#

#
#

#
#
# class InstructionScreen(BaseScreen):
#
#     def on_pre_enter(self, *args):
#         if platform == 'android':
#             color_nav = self.theme_cls.primary_color
#             self.app.change_android_color(color_nav=color_nav)
#
#     def on_pre_leave(self, *args):
#         if platform == 'android':
#             self.app.change_android_color()
#
#     def move_to_screen(self, instance, value):
#         if value == 'Purchase via google play store':
#             self.app.root.transition = MDSwapTransition()
#             self.app.root.current = 'buy_coins_screen'
#         elif value == 'View ads':
#             self.app.root.ids.main_screen.show_ads()