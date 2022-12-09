from kivy.clock import Clock
from kivy.loader import Loader
from kivy.uix.screenmanager import FallOutTransition
from kivy.properties import StringProperty, ObjectProperty, BoundedNumericProperty
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.swiper import MDSwiperItem, MDSwiper
from .widget import MyImage
import openai
import threading


class CreateScreen(MDScreen):
    image_section = ObjectProperty()
    option_section = ObjectProperty()
    prompt = StringProperty()
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty('256x256')

    def load_images(self, **kwargs):
        kwargs['spinner'].active = True

        response = openai.Image.create(
            prompt=self.prompt,
            n=self.image_count,
            size=self.image_size,
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
        if all([self.prompt, self.image_count, self.image_size]):

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

            if self.image_count == 1:
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


class OpenImageScreen(MDScreen):

    def back(self, screen):
        self.parent.transition = FallOutTransition()
        self.parent.current = screen




