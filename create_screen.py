from kivy.graphics import Color, Rectangle
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import RiseInTransition
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.swiper import MDSwiperItem, MDSwiper
import openai


class MyImage(AsyncImage):
    sm = ObjectProperty()

    def on_touch_up(self, touch):
        print(self.collide_point(*touch.pos))
        if self.collide_point(*touch.pos):
            self.full_screen()

    def collide_point(self, x, y):
        width, height = self.norm_image_size
        left = self.x + (self.width - width) / 2
        right = self.right - (self.right - (left + width))
        top = height
        return left <= x <= right and self.y <= y <= top

    def full_screen(self):
        self.sm.ids.open_img_screen.ids.full_image.source = self.source
        self.sm.transition = RiseInTransition()
        self.sm.current = 'open_img_screen'


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
        if self.option_section.prompt:

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

                layout = MDRelativeLayout(
                    id='box_image',
                )

                image = MyImage(
                    sm=self.parent,
                    source='1024x1024.jpg',  # source=f'{url}'
                    allow_stretch=True,
                )

                layout.add_widget(image)

                self.image_section.add_widget(layout)
            elif self.option_section.image_count > 1:  # len(response['data']) > 1
                swiper = MDSwiper(id='swiper_image')

                for el in range(self.option_section.image_count):  # response['data']
                    # url = el.get('url')

                    item = MDSwiperItem()

                    image = MyImage(
                        sm=self.parent,
                        source='1024x1024.jpg',  # source=f'{url}'
                        allow_stretch=True,
                    )

                    item.add_widget(image)

                    swiper.add_widget(item)

                self.image_section.add_widget(swiper)


