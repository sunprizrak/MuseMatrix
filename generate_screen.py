from kivy.uix.image import AsyncImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
import openai
from kivymd.uix.screen import MDScreen
from kivymd.uix.swiper import MDSwiperItem, MDSwiper


class ImageSection(MDBoxLayout):
    pass


class OptionSection(MDBoxLayout):
    prompt = StringProperty()
    image_count = NumericProperty()
    image_size = StringProperty()


class GenerateScreen(MDScreen):
    image_section = ObjectProperty()
    option_section = ObjectProperty()
    count = 0

    def __init__(self, **kwargs):
        super(GenerateScreen, self).__init__(**kwargs)
        GenerateScreen.count += 1
        print(f'{self.__class__.__name__} {GenerateScreen.count}')

    def generate(self):
        # openai.api_key = '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'
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

            layout = MDBoxLayout(id='box_image')
            layout.add_widget(AsyncImage(source=f'1024x1024.jpg'))  # source=f'{url}'

            self.image_section.add_widget(layout)
        elif self.option_section.image_count > 1:  # len(response['data']) > 1
            swiper = MDSwiper(id='swiper_image')

            for el in range(self.option_section.image_count):  # response['data']
                # url = el.get('url')

                item = MDSwiperItem()
                item.add_widget(AsyncImage(source=f'default.jpg'))  # source=f'{url}'

                swiper.add_widget(item)

            self.image_section.add_widget(swiper)


