from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import RiseInTransition
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.swiper import MDSwiperItem, MDSwiper
import openai


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
    image_count = NumericProperty()
    image_size = StringProperty()


class CreateScreen(MDScreen):
    image_section = ObjectProperty()
    option_section = ObjectProperty()

    def create(self):
        if self.option_section.prompt:

            # response = openai.Image.create(
            #     prompt=self.option_section.prompt,
            #     n=self.option_section.image_count,
            #     size=self.option_section.image_size,
            # )
            #
            # print(response)

            for widget in self.image_section.children:
                try:
                    if widget.id == 'box_image' or widget.id == 'swiper_image':
                        self.image_section.remove_widget(widget)
                except Exception:
                    pass

            if self.option_section.image_count == 1:    # len(response['data']) == 1
                # url = response['data'][0].get('url')

                layout = MDRelativeLayout(
                    id='box_image',
                )

                image = MyImage(
                    sm=self.parent,
                    #source=f'{url}',
                    source='https://oaidalleapiprodscus.blob.core.windows.net/private/org-2DPiZYNZodBycS9fvh0ao9aE/user-SsGnIAyK6zK7DJGy26seC8ME/img-eLAOkNq3A1plPT538vUCcY1M.png?st=2022-12-06T13%3A38%3A35Z&se=2022-12-06T15%3A38%3A35Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2022-12-06T13%3A26%3A55Z&ske=2022-12-07T13%3A26%3A55Z&sks=b&skv=2021-08-06&sig=LJPVQ5K0tSXkbvImCXSWgXGIRdnPVtQho2X8s7rba9Q%3D',
                    mipmap=True,
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
                        #source=f'{url}',
                        source='https://oaidalleapiprodscus.blob.core.windows.net/private/org-2DPiZYNZodBycS9fvh0ao9aE/user-SsGnIAyK6zK7DJGy26seC8ME/img-eLAOkNq3A1plPT538vUCcY1M.png?st=2022-12-06T13%3A38%3A35Z&se=2022-12-06T15%3A38%3A35Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2022-12-06T13%3A26%3A55Z&ske=2022-12-07T13%3A26%3A55Z&sks=b&skv=2021-08-06&sig=LJPVQ5K0tSXkbvImCXSWgXGIRdnPVtQho2X8s7rba9Q%3D',
                        mipmap=True,
                        allow_stretch=True,
                    )

                    item.add_widget(image)

                    swiper.add_widget(item)

                self.image_section.add_widget(swiper)


