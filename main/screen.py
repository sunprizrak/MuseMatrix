from kivy.uix.screenmanager import FallOutTransition
from kivy.properties import StringProperty, ObjectProperty, BoundedNumericProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.swiper import MDSwiperItem, MDSwiper
from .widget import MyImage
from .controller import OpenAIController
from main.controller import ImageController
import io
from kivy.core.image import Image as CoreImage


class MainScreen(MDScreen):
    core = ObjectProperty()
    image_section = ObjectProperty()
    option_section = ObjectProperty()
    prompt = StringProperty()
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.image_controller = ImageController(screen=self)

    def create(self):

        def callback(request, response):
            self.ids.spinner.active = False

            if len(response['data']) == 1:
                url = response['data'][0].get('url')

                layout = MDBoxLayout(padding=[0, 15, 0, 15])

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

            self.openai_controller.get_image(
                prompt=self.prompt,
                image_count=self.image_count,
                image_size=self.image_size,
                callback=callback,
            )


class OpenImageScreen(MDScreen):
    core = ObjectProperty()

    def back(self, screen):
        self.parent.transition = FallOutTransition()
        self.parent.current = screen

    def download(self, texture):

        def save_image():
            image = CoreImage(texture)
            image.save('./gallery/test.png')
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



