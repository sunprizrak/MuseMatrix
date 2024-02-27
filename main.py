import logging
from kivy.core.image import Image as CoreImage
from kivy.core.text import LabelBase
from kivy.loader import Loader
from kivy.metrics import dp
from kivy.uix.image import Image

from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.button import MDFabButton
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.transition import MDSlideTransition
from kivy.utils import platform
from kivy.clock import mainthread, Clock
from kivy.logger import Logger
from kivymd.utils.set_bars_colors import set_bars_colors
from kivy.storage.jsonstore import JsonStore
from controller.user import UserController
from settings import ID_REWARD_INTERSTITIAL
import base64
import io
import os
import asynckivy as ak

__version__ = '0.78'

logging.getLogger('PIL').setLevel(logging.WARNING)
os.environ["KIVY_AUDIO"] = "ffpyplayer"

if platform == 'android':
    from android import api_version
    from android.permissions import request_permissions, check_permission, Permission
    from androidstorage4kivy import SharedStorage, Chooser
    from kivads import KivAds, RewardedInterstitial
elif platform == 'linux':
    Window.size = (360, 600)


class MainApp(MDApp):

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.title = "MuseMatrix"
        self.dialog = None
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )

        if platform == 'android':
            self.ads = KivAds()
            self.reward_interstitial = RewardedInterstitial(
                ID_REWARD_INTERSTITIAL, self.reward_callback
            )
            self.ss = SharedStorage()
            self.storage = JsonStore(f"{self.ss.get_cache_dir()}/storage.json")
            self.chooser = Chooser(self.chooser_callback)

            if api_version >= 33:
                self.permissions = [Permission.READ_MEDIA_IMAGES, Permission.READ_MEDIA_AUDIO]
            else:
                self.permissions = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE]

        elif platform == 'linux':
            self.storage = JsonStore('storage.json')

    def build(self):
        self.theme_initial()

        if platform == 'android':
            if not self.check_android_permissions:
                self.req_android_permissions()

        Window.softinput_mode = 'below_target'
        Window.bind(on_keyboard=self.key_input)

        kv_file = Builder.load_file('kv_files/layout.kv')
        return kv_file

    def on_start(self):
        super().on_start()
        ak.start(self.check_user_authentication())
        Clock.schedule_once(self.change_android_color)

    def on_resume(self):
        if platform == 'android':
            self.load_ads_video()
        pass

    def on_pause(self):
        return True

    def theme_initial(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Ghostwhite"
        LabelBase.register(name='Hacked', fn_regular='assets/font/hacked.ttf')

    @staticmethod
    def get_version():
        return __version__

    def change_android_color(self, *args, **kwargs):
        if platform == 'android':
            color_stat = self.theme_cls.backgroundColor
            color_nav = self.theme_cls.backgroundColor
            if kwargs.get('color_stat'):
                color_stat = kwargs.get('color_stat')
            if kwargs.get('color_nav'):
                color_nav = kwargs.get('color_nav')

            set_bars_colors(color_stat, color_nav)

    def load_ads_video(self):
        if platform == 'android':
            self.reward_interstitial.load(ID_REWARD_INTERSTITIAL)

    def reward_callback(self, *args):
        user_controller = UserController()
        reward_name = 'coin'
        reward_amount = 1
        total_amount = user_controller.user.coin + reward_amount

        def _on_success(request, response):
            self.load_ads_video()
            user_controller.user.update(data_user=response)
            screen = self.root.get_screen('main_screen')
            screen.coin = user_controller.user.coin

        user_controller.update_user(fields={reward_name: total_amount}, on_success=_on_success)

    async def check_user_authentication(self):
        if self.storage.exists('auth_token'):
            user_controller = UserController()
            user_controller.authorized()

    @property
    def check_android_permissions(self):
        if all(list(map(check_permission, self.permissions))):
            return True
        else:
            return False

    def req_android_permissions(self):
        request_permissions(self.permissions)

    def chooser_callback(self, shared_file_list):
        try:
            for shared_file in shared_file_list:
                private_file = self.ss.copy_from_shared(shared_file)
                self.select_path(path=private_file)
        except Exception as e:
            Logger.warning('SharedStorageExample.chooser_callback():')
            Logger.warning(str(e))

    def file_manager_open(self):
        if platform == 'linux':
            self.file_manager.show(os.path.expanduser('~'))
            self.manager_open = True
            self.file_manager.ext.extend(['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'])
        elif platform == 'android':
            if self.check_android_permissions:
                if self.root.current == 'speech_to_text_screen':
                    self.chooser.choose_content('audio/*')
                else:
                    self.chooser.choose_content('image/*')
            else:
                self.req_android_permissions()

    @mainthread
    def select_path(self, path: str):
        if platform == 'linux':
            self.exit_manager()

        screen = self.root.get_screen(self.root.current)

        if screen.name == 'speech_to_text_screen':

            if f'.{path.split(".")[-1]}' in ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']:

                if len(path.split('/')[-1]) > 22:
                    sound_name = f'...{path.split("/")[-1][-19:]}'
                else:
                    sound_name = path.split('/')[-1]

                screen.add_sound(path=path, sound_name=sound_name)
        elif screen.name == 'main_screen':
            user_controller = UserController()

            def _on_success(request, response):
                user_controller.user.update(data_user=response)
                screen.avatar = user_controller.user.avatar

            image = CoreImage(path)

            data = io.BytesIO()
            image.save(data, fmt='png')
            png_bytes = data.read()

            im_b64 = base64.b64encode(png_bytes).decode('UTF-8')

            user_controller.update_user(fields={'avatar': im_b64}, on_success=_on_success)
        else:
            if f'.{path.split(".")[-1]}' in ['.jpg', '.jpeg', '.jpe', '.jfif', '.png', '.ico']:
                screen.add_image(path=path)

    def exit_manager(self, *args):
        if platform == 'linux':
            self.manager_open = False
            self.file_manager.close()

    def show_dialog(self, title=None, sup_text=None, button=None, content=None):
        self.dialog = MDDialog(
            MDDialogButtonContainer(
                Widget(),
                button,
                MDFabButton(
                    icon='close-thick',
                    style='small',
                    on_release=self.close_dialog,
                ),
                spacing='8dp',
            ),
            size_hint_x=.9,
            theme_bg_color='Custom',
            md_bg_color=self.theme_cls.backgroundColor,
            radius=dp(25),
        )

        if title:
            self.dialog.add_widget(
                MDDialogHeadlineText(
                    text=title,
                    theme_font_name="Custom",
                    font_name='Hacked',
                ),
            )
        else:
            self.dialog.add_widget(
                MDDialogHeadlineText(
                    text='Notice!',
                ),
            )

        if sup_text:
            self.dialog.add_widget(
                MDDialogSupportingText(
                    text=sup_text,
                    theme_font_name="Custom",
                    font_name='Hacked',
                ),
            )

        if content:
            self.dialog.add_widget(
                MDDialogContentContainer(
                    content,
                ),
            )

        self.dialog.open()

    def close_dialog(self, inst):
        self.dialog.dismiss()

    def back(self, screen):
        self.root.transition = MDSlideTransition()
        self.root.transition.direction = 'right'
        self.root.current = screen

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            if self.root.current not in ('start_screen', 'main_screen'):
                if self.root.current in ('reg_screen', 'login_screen'):
                    self.back(screen='start_screen')
                elif self.root.current == 'open_img_screen':
                    screen = self.root.get_screen(self.root.current)
                    screen.back(screen=screen.ids.full_image.back_screen)
                else:
                    self.back(screen='main_screen')
                return True
            else:
                return False
        else:
            return False


if __name__ == '__main__':
    MainApp().run()