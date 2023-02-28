from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.theming import ThemeManager
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.uix.transition import MDSlideTransition
from kivy.utils import platform
from kivy.clock import mainthread
from kivy.logger import Logger
import os
from shutil import rmtree
from main.settings import storage
from users.controller import UserController

if platform == 'android':
    from android import api_version
    from android.permissions import request_permissions, check_permission, Permission
    from androidstorage4kivy import SharedStorage, Chooser


class CustomThemeManager(ThemeManager):
    def __init__(self, **kwargs):
        super(CustomThemeManager, self).__init__(**kwargs)
        self.font_styles.update({
            "H1": ["Hacked", 96, False, -1.5],
            "H2": ["Hacked", 60, False, -0.5],
            "H3": ["Hacked", 48, False, 0],
            "H4": ["Hacked", 34, False, 0.25],
            "H5": ["Hacked", 24, False, 0],
            "H6": ["Hacked", 20, False, 0.15],
            "Subtitle1": ["Hacked", 16, False, 0.15],
            "Subtitle2": ["Hacked", 14, False, 0.1],
            "Body1": ["Hacked", 16, False, 0.5],
            "Body2": ["Hacked", 14, False, 0.25],
            "Button": ["Hacked", 14, True, 1.25],
            "Caption": ["Hacked", 12, False, 0.4],
            "Overline": ["Hacked", 10, True, 1.5],
            'Message': ['Roboto', 16, False, 0.5],
        })
        LabelBase.register(name='Hacked', fn_regular='main/font/hacked.ttf')


class ArtAIApp(MDApp):

    def __init__(self, **kwargs):
        super(ArtAIApp, self).__init__(**kwargs)
        self.theme_cls = CustomThemeManager()
        self.dialog = None
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )

        if platform == 'android':
            self.ss = SharedStorage()
            self.chooser = Chooser(self.chooser_callback)
            if api_version > 29:
                self.permissions = [Permission.READ_EXTERNAL_STORAGE]
            else:
                self.permissions = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]

    def build(self):
        if platform == 'linux':
            Window.size = (360, 600)
        elif platform == 'android':
            if not self.check_android_permissions():
                self.req_android_permissions()

            cache = self.ss.get_cache_dir()

            if cache and os.path.exists(cache):
                rmtree(cache)

        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Purple'

        Window.softinput_mode = 'below_target'
        Window.bind(on_keyboard=self.key_input)

        kv_file = Builder.load_file('main/kv/layout.kv')
        return kv_file

    def on_start(self):
        self.check_user_authentication()

    def check_user_authentication(self):
        if storage.exists('auth_token'):
            user_controller = UserController(screen=self.root.children[0])
            user_controller.authorized()

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
        elif platform == 'android':
            if self.check_android_permissions():
                self.chooser.choose_content('image/*')
            else:
                self.req_android_permissions()

    @mainthread
    def select_path(self, path: str):
        if platform == 'linux':
            self.exit_manager()

        toast(path)

        for screen in self.root.children:
            if screen.name == self.root.current:
                screen.add_image(path=path)

    def exit_manager(self, *args):
        if platform == 'linux':
            self.manager_open = False
            self.file_manager.close()

    def show_dialog(self, button=None):
        self.dialog = MDDialog(
            title='Notice!',
            type='custom',
            radius=[20, 7, 20, 7],
            buttons=[
                button,
                MDFlatButton(
                    text="Close",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.close_dialog,
                ),
            ],
        )
        self.dialog.open()

    def close_dialog(self, inst):
        self.dialog.dismiss()

    def back(self, screen):
        if self.root.current in ('login_screen', 'reg_screen', 'change_password_screen'):
            for scr in self.root.screens:
                if scr.name == self.root.current:
                    for field_name in scr.ids.keys():
                        if 'field' in field_name:
                            scr.ids[field_name].text = ''
        elif self.root.current == 'chat_gpt_screen':
            Window.softinput_mode = 'below_target'

        self.root.transition = MDSlideTransition()
        self.root.transition.direction = 'right'
        self.root.current = screen

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            if self.root.current not in ('start_screen', 'main_screen'):
                if self.root.current in ('reg_screen', 'login_screen'):
                    self.back(screen='start_screen')
                elif self.root.current == 'open_img_screen':
                    for scr in self.root.screens:
                        if scr.name == self.root.current:
                            scr.back(screen=scr.ids.full_image.back_screen)
                else:
                    self.back(screen='main_screen')
                return True
            else:
                return False
        else:
            return False


if __name__ == '__main__':
    ArtAIApp().run()