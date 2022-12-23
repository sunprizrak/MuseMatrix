from kivy.uix.screenmanager import FallOutTransition
from kivy.properties import StringProperty, ObjectProperty, BoundedNumericProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.swiper import MDSwiperItem, MDSwiper
from kivy.core.image import Image as CoreImage
from kivymd.uix.transition import MDSlideTransition

from users.controller import UserController
from .widget import MyImage
from .controller import OpenAIController
from main.controller import ImageController
import io
import base64
import random


class MainScreen(MDScreen):
    pass

    # def add_image(self, path):
    #
    #     layout = MDBoxLayout(
    #         padding=[0, 15, 0, 15],
    #     )
    #
    #     image = MyImage(
    #         sm=self.parent,
    #         disabled=True,
    #         source=path,
    #         allow_stretch=True,
    #         mipmap=True,
    #     )
    #
    #     layout.add_widget(image)
    #
    #     self.image_edit_section.add_widget(layout)


class CreateImageScreen(MDScreen):
    image_section = ObjectProperty()
    option_section = ObjectProperty()
    prompt = StringProperty()
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')

    def __init__(self, **kwargs):
        super(CreateImageScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.image_controller = ImageController(screen=self)

    def create(self):

        def callback(request, response):
            self.ids.spinner.active = False

            if len(response['data']) == 1:
                url = response['data'][0].get('url')

                layout = MDBoxLayout(
                    padding=[0, 15, 0, 15],
                )

                image = MyImage(
                    sm=self.parent,
                    source=url,
                    allow_stretch=True,
                    mipmap=True,
                )

                layout.add_widget(image)

                self.ids.image_section.add_widget(layout)
            elif len(response['data']) > 1:
                swiper = MDSwiper()

                for el in response['data']:
                    url = el.get('url')

                    item = MDSwiperItem()

                    image = MyImage(
                        sm=self.parent,
                        source=url,
                        mipmap=True,
                        allow_stretch=True,
                    )

                    item.add_widget(image)
                    swiper.add_widget(item)

                self.ids.image_section.add_widget(swiper)

        if all([self.prompt, self.image_count, self.image_size]):

            for widget in self.image_section.children:
                if isinstance(widget, MDBoxLayout) or isinstance(widget, MDSwiper):
                    self.image_section.remove_widget(widget)

            self.ids.spinner.active = True

            self.openai_controller.image_generation(
                prompt=self.prompt,
                image_count=self.image_count,
                image_size=self.image_size,
                callback=callback,
            )


class CollectionScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(CollectionScreen, self).__init__(**kwargs)
        self.image_controller = ImageController(screen=self)

        menu_items = [
            {
                'text': 'Choose all',
                'viewclass': 'OneLineListItem',
                'on_release': lambda: (self.ids.selection_list.selected_all(), self.menu.dismiss()),
            }
        ]

        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=2.5,
        )

    def menu_callback(self, button):
        self.menu.caller = button
        self.menu.open()

    def delete_images(self, widget_list):
        images_id = [widget.children[1].img_id for widget in widget_list]

        def del_images():
            self.image_controller.del_images(images_id=images_id, widget_list=widget_list)
            self.core.dialog.dismiss()

        button = MDFlatButton(
            text="Delete",
            theme_text_color="Custom",
            text_color=self.core.theme_cls.primary_color,
            on_release=lambda x: del_images(),
        )

        self.core.show_dialog(button=button)
        self.core.dialog.title = 'Delete'
        self.core.dialog.text = 'Are you sure you want to delete?'


class OpenImageScreen(MDScreen):
    core = ObjectProperty()

    def __init__(self, **kwargs):
        super(OpenImageScreen, self).__init__(**kwargs)
        self.user_controller = UserController(screen=self)
        self.image_controller = ImageController(screen=self)

    def back(self, screen):
        if len(self.ids.app_bar.right_action_items) > 1:
            self.ids.app_bar.right_action_items.remove(self.ids.app_bar.right_action_items[0])
        self.parent.transition = FallOutTransition()
        self.parent.current = screen

    def download(self, img):

        def save_image():
            image = CoreImage(img.texture)

            if img.back_screen == 'create_image_screen':
                data = io.BytesIO()
                image.save(data, fmt='png')
                png_bytes = data.read()
                im_b64 = base64.b64encode(png_bytes).decode('utf-8')

                data_image = {
                    'user': self.user_controller.user.id,
                    'source': im_b64,
                    'description': self.core.root.ids.create_image_screen.prompt,
                }

                self.image_controller.save_image(data_image=data_image)

            image.save(f"./gallery/{''.join(['' + str(random.randint(0, 9)) for x in range(9)])}.png")

            self.core.dialog.dismiss()

        button = MDFlatButton(
            text="Save",
            theme_text_color="Custom",
            text_color=self.core.theme_cls.primary_color,
            on_release=lambda x: save_image(),
        )

        self.core.show_dialog(button=button)
        self.core.dialog.title = 'Save image'
        self.core.dialog.text = 'Do you want to save the picture?'

    def delete(self, img_id, widget):

        def del_image():
            self.image_controller.del_image(image_id=img_id, widget=widget)
            self.core.dialog.dismiss()

        button = MDFlatButton(
            text="Delete",
            theme_text_color="Custom",
            text_color=self.core.theme_cls.primary_color,
            on_release=lambda x: del_image(),
        )

        self.core.show_dialog(button=button)
        self.core.dialog.title = 'Delete'
        self.core.dialog.text = 'Are you sure you want to delete??'