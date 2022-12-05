from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.swiper import MDSwiperItem, MDSwiper
import openai


class ImageSection(MDBoxLayout):
    pass


class OptionSection(MDBoxLayout):
    prompt = StringProperty()
    image_count = NumericProperty()
    image_size = StringProperty()


class CreateScreen(MDScreen):
    image_section = ObjectProperty()
    option_section = ObjectProperty()
    count = 0

    def __init__(self, **kwargs):
        super(CreateScreen, self).__init__(**kwargs)
        CreateScreen.count += 1
        print(f'{self.__class__.__name__} {CreateScreen.count}')

    def create(self):
        if all([self.option_section.prompt, self.option_section.image_size, self.option_section.image_count]):

            # openai.api_key = ''
            # response = openai.Image.create(
            #     prompt=self.option_section.prompt,
            #     n=self.option_section.image_count,
            #     size=self.option_section.image_size,
            # )
            # print(response)

            for widget in self.image_section.children:
                try:
                    if widget.id == 'box_image' or widget.id == 'swiper_image':
                        self.image_section.remove_widget(widget)
                except Exception:
                    pass

            if self.option_section.image_count == 1:
                # url = response['data'][0].get('url')
                layout = MDRelativeLayout(id='box_image')

                button = Button(
                    background_color=(1, 1, 1, 0),
                    on_release=lambda x: setattr(self.parent, 'current', 'open_img_screen'),
                )

                layout.add_widget(button)
                layout.add_widget(AsyncImage(
                    source='default.jpg',  # source=f'{url}'
                    mipmap=True,
                    keep_ratio=False,
                    allow_stretch=True,
                ))

                self.image_section.add_widget(layout)

            elif self.option_section.image_count > 1:  # len(response['data']) > 1
                swiper = MDSwiper(id='swiper_image')

                for el in range(self.option_section.image_count):  # response['data']
                    # url = el.get('url')

                    item = MDSwiperItem()
                    item.add_widget(AsyncImage(source=f'default.jpg'))  # source=f'{url}'

                    swiper.add_widget(item)

                self.image_section.add_widget(swiper)


