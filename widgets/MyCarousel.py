from kivy.properties import ListProperty
from kivy.uix.carousel import Carousel


class MyCarousel(Carousel):
    saved_images = ListProperty()

    def __init__(self, **kwargs):
        super(MyCarousel, self).__init__(**kwargs)