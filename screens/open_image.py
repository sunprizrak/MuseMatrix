import os
import uuid

from kivy.core.image import Image as CoreImage
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.screenmanager import FallOutTransition
from kivymd.uix.appbar import MDActionBottomAppBarButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivy.utils import platform
from controller.image import ImageController
from controller.user import UserController
from .layout import BaseScreen

if platform == 'android':
    from kivymd.toast.androidtoast import toast


class OpenImageScreen(BaseScreen):
    back_screen = StringProperty()

    def __init__(self, **kwargs):
        super(OpenImageScreen, self).__init__(**kwargs)
        self.user_controller = UserController()
        self.image_controller = ImageController()

    def on_pre_enter(self, *args):
        screen = self.app.root.get_screen(self.back_screen)
        images = []

        if self.back_screen == 'collection_screen':
            images = [smart_tile.image for smart_tile in screen.ids.selection_list.children]

        images.reverse()

        for obj in images:

            image = FitImage(
                texture=obj.texture,
                fit_mode='contain',
                mipmap=True,
                pos_hint={'center_y': .5}
            )

            if self.back_screen == 'collection_screen':
                image.img_id = obj.img_id
                image.pre_parent = obj.parent

            self.ids.carousel.add_widget(image)

        self.ids.bottom_bar.action_items = [
            MDActionBottomAppBarButton(
                icon="download",
                on_release=lambda x: self.download(img=self.ids.carousel.current_slide),
            ),

            MDActionBottomAppBarButton(
                icon='delete',
                on_release=lambda x: self.delete(
                    img_id=self.ids.carousel.current_slide.img_id,
                    widget_selection=self.ids.carousel.current_slide.pre_parent,
                ),
            ),
        ]

    def on_enter(self, *args):
        app_bar = self.ids.app_bar_title
        carousel = self.ids.carousel

        app_bar.text = 'x'.join(str(carousel.current_slide.texture_size).split(', '))

        def _change_appbar_title(instance, value):
            if value:
                app_bar.text = 'x'.join(str(value.texture_size).split(', '))

        carousel.bind(current_slide=_change_appbar_title)

    def on_leave(self, *args):
        self.ids.carousel.clear_widgets()

    def back(self, screen):
        self.app.root.transition = FallOutTransition()
        self.app.root.current = screen

    def download(self, img):
        def _save_image():
            image = CoreImage(img.texture)

            if platform == 'android':
                private_path = os.path.join(self.app.ss.get_cache_dir(), f'{str(uuid.uuid4())}.png')

                image.save(private_path)

                if os.path.exists(private_path):
                    self.app.ss.copy_to_shared(private_path)

            self.app.dialog.dismiss()
            toast(text='image saved')

        button = MDButton(
            MDButtonText(
                text='download',
                theme_text_color="Custom",
                text_color='white',
                theme_font_name="Custom",
                font_name='Hacked',
            ),
            style='filled',
            theme_bg_color='Custom',
            md_bg_color='green',
            on_release=lambda x: _save_image(),
        )

        content = MDBoxLayout(
            MDLabel(
                text='Do you want to download the picture?',
                padding=[0, dp(10), 0, 0],
            ),
        )

        self.app.show_dialog(
            title='Download image',
            button=button,
            content=content,
        )

    def delete(self, img_id, widget_selection):
        def _del_image():
            def _on_success(request, response):
                screen = self.app.root.get_screen('collection_screen')

                self.image_controller.object.delete_image(image_id=img_id)
                screen.ids.selection_list.remove_widget(widget_selection)
                self.ids.carousel.remove_widget(self.ids.carousel.current_slide)

                for index, smart_tile in enumerate(reversed(screen.ids.selection_list.children)):
                    smart_tile.image.index = index

            def _on_failure(request, response):
                print(response)

            self.image_controller.del_image(
                image_id=img_id,
                on_success=_on_success,
                on_failure=_on_failure)

            self.app.dialog.dismiss()

        button = MDButton(
            MDButtonText(
                text='delete',
                theme_text_color="Custom",
                text_color='white',
                theme_font_name="Custom",
                font_name='Hacked',
            ),
            style='filled',
            theme_bg_color='Custom',
            md_bg_color='red',
            on_release=lambda x: _del_image(),
        )

        content = MDBoxLayout(
            MDLabel(
                text='Are you sure you want to delete?',
                padding=[0, dp(10), 0, 0],
            ),
        )

        self.app.show_dialog(
            title='Delete',
            button=button,
            content=content,
        )