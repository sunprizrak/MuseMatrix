from kivy.uix.image import AsyncImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty
import openai
from kivymd.uix.swiper import MDSwiperItem, MDSwiper


class MyImage(AsyncImage):

    def __init__(self, **kwargs):
        super(MyImage, self).__init__(**kwargs)
        self.size = self.texture_size


class JustGenerate(MDBoxLayout):
    prompt = StringProperty()
    image_count = NumericProperty()
    image_size = StringProperty()

    def generate(self):
        # openai.api_key = ''
        # response = openai.Image.create(
        #     prompt=self.prompt,
        #     n=self.image_count,
        #     size=self.image_size,
        # )
        # print(response)

        for widget in self.children:
            try:
                if widget.id == 'box_image' or widget.id == 'swiper_image':
                    self.remove_widget(widget)
            except Exception:
                pass

        if self.image_count > 1:  # len(response['data']) > 1
            swiper = MDSwiper(id='swiper_image')

            for el in range(self.image_count):   #response['data']
                # url = el.get('url')

                item = MDSwiperItem()
                item.add_widget(MyImage(source=f'default.jpg'))

                swiper.add_widget(item)

            self.add_widget(swiper, index=100)
        else:
            # url = response['data'][0].get('url')
            # self.parent.ids.box_image.add_widget(
            #     MyImage(source=f'{url}', size=self.image_size)
            # )

            box = MDBoxLayout(
                id='box_image',
                pos_hint={'center_x': .5},
                size_hint=(None, None),
                size=(256, 256)
            )

            box.add_widget(MyImage(source=f'default.jpg'))

            self.add_widget(box, index=100)




