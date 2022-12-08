from kivy.clock import Clock
from kivy.loader import Loader
from kivy.uix.image import AsyncImage, Image
from kivy.uix.screenmanager import RiseInTransition
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, ObjectProperty, BoundedNumericProperty
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.swiper import MDSwiperItem, MDSwiper
import openai
import threading
import time


class MyImage(AsyncImage):
    sm = ObjectProperty()

    def on_touch_up(self, touch):
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


class ImageSection(MDRelativeLayout):
    pass


class OptionSection(MDBoxLayout):
    prompt = StringProperty()
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')


class CreateScreen(MDScreen):
    image_section = ObjectProperty()
    option_section = ObjectProperty()

    def load_images(self, **kwargs):
        kwargs['spinner'].active = True

        response = openai.Image.create(
            prompt=self.option_section.prompt,
            n=self.option_section.image_count,
            size=self.option_section.image_size,
        )

        kwargs['spinner'].active = False

        if len(response['data']) == 1:
            url = response['data'][0].get('url')
            kwargs['image'].source = url  # source='https://loremflickr.com/320/240/cat'
        elif len(response['data']) > 1:
            count = 0
            for el in response['data']:  # response['data']
                url = el.get('url')
                kwargs['swiper'].children[0].children[count].children[0].children[0].source = url
                count += 1

    def create(self):
        if all([self.option_section.prompt, self.option_section.image_count, self.option_section.image_size]):

            spinner = MDSpinner(
                size_hint=(None, None),
                size=(38, 38),
                pos_hint={'center_x': .5, 'center_y': .5},
                active=False,
            )

            kwargs = {}

            for widget in self.image_section.children:
                if isinstance(widget, MDRelativeLayout) or isinstance(widget, MDSwiper):
                    self.image_section.remove_widget(widget)

            if self.option_section.image_count == 1:
                layout = MDRelativeLayout()

                image = MyImage(
                    sm=self.parent,
                    mipmap=True,
                    allow_stretch=True,
                )

                layout.add_widget(spinner, index=0)
                layout.add_widget(image, index=1)

                self.image_section.add_widget(layout)

                kwargs={'spinner': spinner, 'image': image}
            elif self.option_section.image_count > 1:
                layout = MDRelativeLayout()
                swiper = MDSwiper()

                for el in range(self.option_section.image_count):
                    item = MDSwiperItem()
                    image = MyImage(
                        sm=self.parent,
                        #source='https://loremflickr.com/320/240/cat',
                        mipmap=True,
                        allow_stretch=True,
                    )

                    item.add_widget(image)
                    swiper.add_widget(item)

                layout.add_widget(spinner, index=0)
                layout.add_widget(swiper, index=1)
                self.image_section.add_widget(layout)

                kwargs = {'swiper': swiper, 'spinner': spinner}

            thr = threading.Thread(target=self.load_images, kwargs=kwargs)
            thr.start()










