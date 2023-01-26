from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.uix.transition import MDSlideTransition
import os


from users.screen import LoginScreen, RegistrateScreen, ProfileScreen
from main.screen import MainScreen
# Window.size = (360, 600)


class ArtAIApp(MDApp):

    def __init__(self, **kwargs):
        super(ArtAIApp, self).__init__(**kwargs)

        self.theme_cls.material_style = 'M3'
        self.dialog = None
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )

    def build(self):
        kv_file = Builder.load_file('./core/kv/layout.kv')
        return kv_file

    def file_manager_open(self):
        self.file_manager.show(os.path.expanduser('~'))
        self.manager_open = True

    def select_path(self, path: str):
        self.exit_manager()
        toast(path)
        if self.root.current == 'edit_image_screen':
            self.root.ids.edit_image_screen.add_image(path=path)
        elif self.root.current == 'variable_image_screen':
            self.root.ids.variable_image_screen.add_image(path=path)

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

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
        self.root.transition = MDSlideTransition()
        self.root.transition.direction = 'right'
        self.root.current = screen


if __name__ == '__main__':
    ArtAIApp().run()