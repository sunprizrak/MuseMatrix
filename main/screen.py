from kivy.uix.screenmanager import FallOutTransition
from kivy.properties import StringProperty, ObjectProperty, BoundedNumericProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.swiper import MDSwiperItem, MDSwiper
from kivy.core.image import Image as CoreImage
from users.controller import UserController
from .widget import MyImage
from .controller import OpenAIController
from main.controller import ImageController
import io
import base64
import random


class MainScreen(MDScreen):
    pass


class CreateImageScreen(MDScreen):
    prompt = StringProperty()
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')
    default_img = ObjectProperty()

    def __init__(self, **kwargs):
        super(CreateImageScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.image_controller = ImageController(screen=self)

    def create(self):

        def callback(request, response):
            self.ids.create_spin.active = False

            if len(response['data']) == 1:
                url = response['data'][0].get('url')

                image = MyImage(
                    sm=self.parent,
                    source=url,
                    allow_stretch=True,
                    mipmap=True,
                )

                self.ids.image_section.add_widget(image)
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

            for widget in self.ids.image_section.children:
                if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                    self.ids.image_section.remove_widget(widget)

            self.ids.image_section.remove_widget(self.default_img)

            self.ids.create_spin.active = True

            self.openai_controller.image_generation(
                prompt=self.prompt,
                image_count=self.image_count,
                image_size=self.image_size,
                callback=callback,
            )


class EditImageScreen(MDScreen):
    prompt = StringProperty()
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')
    image_original = io.BytesIO()
    image_mask = io.BytesIO()

    def __init__(self, **kwargs):
        super(EditImageScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()

    def add_image(self, path):

        image = MyImage(
            sm=self.parent,
            disabled=True,
            source=path,
            allow_stretch=True,
            mipmap=True,
        )

        self.ids.image_section.add_widget(image)

        image_core = CoreImage(image.texture)
        image_core.save(self.image_original, fmt='png')

    def edit_image(self):

        def callback(request, response):
            self.ids.edit_spin.active = False

            if len(response['data']) == 1:
                url = response['data'][0].get('url')

                image = MyImage(
                    sm=self.parent,
                    source=url,
                    allow_stretch=True,
                    mipmap=True,
                )

                self.ids.image_section.add_widget(image)
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

            for widget in self.ids.image_section.children:
                if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
                    if isinstance(widget, MyImage) and widget.disabled:
                        mask_img = self.ids.image_section.children[0].get_mask_image()
                        mask_img.save(self.image_mask, flipped=True, fmt='png')
                    self.ids.image_section.remove_widget(widget)

            self.ids.edit_spin.active = True

            png_image_original = self.image_original.read()
            im_b64_image_original = base64.b64encode(png_image_original).decode('utf-8')

            png_image_mask = self.image_mask.read()
            im_b64_image_mask = base64.b64encode(png_image_mask).decode('utf-8')

            self.openai_controller.image_edit(
                image=im_b64_image_original,
                mask=im_b64_image_mask,
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