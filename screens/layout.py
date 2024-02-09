import base64
import io
from kivy.core.image import Image as CoreImage
from kivy.utils import platform
from kivy.properties import BoundedNumericProperty, StringProperty, NumericProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from controller.image import ImageController
from controller.openai import OpenAIController
from controller.user import UserController
from widgets.MySelectionList import MySmartTile, MySmartTileImage


class BaseScreen(MDScreen):
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.theme_bg_color = 'Custom'


class ImageScreen(BaseScreen):
    image_count = BoundedNumericProperty(1, min=1, max=10, errorhandler=lambda x: 10 if x > 10 else 1)
    image_size = StringProperty()
    price = NumericProperty()

    def __init__(self, **kwargs):
        super(ImageScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.user_controller = UserController()
        self.image_controller = ImageController()

    def save_image(self, widget):
        core_image = CoreImage(widget.texture)

        data = io.BytesIO()
        core_image.save(data, fmt='png')
        png_bytes = data.read()
        im_b64 = base64.b64encode(png_bytes).decode('UTF-8')

        data_image = {
            'user': self.user_controller.user.id,
            'source': im_b64,
        }

        if self.name != 'variable_image_screen':
            data_image['description'] = self.prompt

        def _on_success(request, response):
            self.ids.carousel.saved_images.append(widget)

            image = self.image_controller.object(data_image=response)

            screen = self.app.root.get_screen('collection_screen')

            smart_tile = MySmartTile()

            smart_tile_image = MySmartTileImage(
                source=image.source,
                fit_mode='contain',
                mipmap=True,
                img_id=image.id,
            )
            smart_tile.add_widget(smart_tile_image)

            screen.ids.selection_list.add_widget(smart_tile, index=len(self.image_controller.object.images) - 1 if len(
                self.image_controller.object.images) > 0 else 0)

            for index, smart_tile in enumerate(reversed(screen.ids.selection_list.children)):
                smart_tile.image.index = index

        def _on_failure(request, response):
            print(response)

        self.image_controller.save_image(
            data_image=data_image,
            on_success=_on_success,
            on_failure=_on_failure,
        )

    # def on_pre_enter(self, *args):
    #     if platform == 'android':
    #         color_nav = self.theme_cls.primary_color
    #         self.app.change_android_color(color_nav=color_nav)
    #
    # def on_pre_leave(self, *args):
    #     if platform == 'android':
    #         self.app.change_android_color()