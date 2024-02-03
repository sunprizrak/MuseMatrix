import base64
import io

from kivy.graphics import Color, Line, StencilPush, StencilUse, Rectangle, StencilPop, StencilUnUse
from kivy.properties import StringProperty
from kivy.uix.image import AsyncImage, Image
from kivy.uix.stencilview import StencilView
from kivymd.uix.swiper import MDSwiper

from widgets.EditImage import EditImage
from .layout import ImageScreen
from PIL import Image as PilImage


class EditImageScreen(ImageScreen):
    prompt = StringProperty()
    image_original = io.BytesIO()
    image_mask = io.BytesIO()

    def add_image(self, path):
        self.ids.add_image_button.disabled = True
        self.ids.add_image_button.opacity = 0

        # image = EditImage(
        #     source=path,
        #     fit_mode='contain',
        #     mipmap=True,
        #     pos_hint={'center_x': .5, 'center_y': .5},
        # )
        #
        # self.ids.image_section.add_widget(image)
        # if len(self.ids.edit_top_bar.right_action_items) == 0:
        #     self.ids.edit_top_bar.right_action_items.append(["autorenew", lambda x: self.reload_image()])
        #     self.ids.edit_top_bar.right_action_items.append(["broom", lambda x: self.clear_selection()])
        #
        # with PilImage.open(path) as img:
        #     new = img.resize(size=(256, 256))
        #     new.save(self.image_original, format='png')

    def test_edit(self):
        # mask = self.ids.test.get_mask_image()
        # mask_data = io.BytesIO()
        # mask.save(mask_data, flipped=True, fmt='png')
        # with PilImage.open(mask_data) as img:
        #     new = img.resize(size=(256, 256))
        #     new.save('test_edit_image/test.png')
        self.ids.test.get_mask_image()

#
    def edit_image(self):

        # def _on_success(request, response):
        #     self.ids.edit_spin.active = False
        #
        #     if 'data' in response:
        #         self.user_controller.user.coin = response['coin']
        #         self.app.root.ids.main_screen.coin = self.user_controller.user.coin
        #
        #         if len(response['data']) == 1:
        #             url = response['data'][0].get('url')
        #
        #             image = MyImage(
        #                 source=url,
        #                 fit_mode='contain',
        #                 mipmap=True,
        #             )
        #
        #             self.ids.image_section.add_widget(image)
        #         elif len(response['data']) > 1:
        #             swiper = MDSwiper()
        #
        #             for el in response['data']:
        #                 url = el.get('url')
        #
        #                 item = MDSwiperItem()
        #
        #                 image = MyImage(
        #                     source=url,
        #                     mipmap=True,
        #                     fit_mode='contain',
        #                 )
        #
        #                 item.add_widget(image)
        #                 swiper.add_widget(item)
        #
        #             self.ids.image_section.add_widget(swiper)
        #     elif 'notice' in response:
        #         self.ids.add_image_button.disabled = False
        #         self.ids.edit_top_bar.right_action_items = []
        #
        #         self.app.show_dialog()
        #         self.app.dialog.title = 'Notice!'
        #         self.app.dialog.text = response['notice']
        #
        # def _output_error(error):
        #     self.ids.edit_spin.active = False
        #     self.ids.add_image_button.disabled = False
        #
        #     self.ids.edit_top_bar.right_action_items = []
        #
        #     if type(error) is dict:
        #         if {'error'} & set(error):
        #             self.app.show_dialog()
        #             self.app.dialog.text = error.get('error')
        #
        # def _on_error(request, error):
        #     _output_error(error)
        #
        # def _on_failure(request, response):
        #     _output_error(response)

        self.image_original.seek(0)
        if len(self.image_original.getvalue()) > 0:
            if all([self.prompt, self.image_count, self.image_size]):
                for widget in self.ids.image_section.children:
                    if isinstance(widget, EditImage) or isinstance(widget, MDSwiper):
                        if isinstance(widget, EditImage) and widget.disabled:
                            mask_img = self.ids.image_section.children[0].get_mask_image()
                            mask_data = io.BytesIO()
                            mask_img.save(mask_data, flipped=True, fmt='png')

                            with PilImage.open(mask_data) as img:
                                new = img.resize(size=(256, 256))
                                new.save(self.image_mask, format='png')

                        self.ids.image_section.remove_widget(widget)

                self.ids.add_image_button.disabled = True
                self.ids.edit_spin.active = True

                self.image_original.seek(0)
                png_image_original = self.image_original.getvalue()
                im_b64_image_original = base64.b64encode(png_image_original).decode('UTF-8')

                self.image_mask.seek(0)
                png_image_mask = self.image_mask.getvalue()
                im_b64_image_mask = base64.b64encode(png_image_mask).decode('UTF-8')

                # self.openai_controller.image_edit(
                #     image=im_b64_image_original,
                #     mask=im_b64_image_mask,
                #     prompt=self.prompt,
                #     image_count=self.image_count,
                #     image_size=self.image_size,
                #     on_success=_on_success,
                #     on_error=_on_error,
                #     on_failure=_on_failure,
                # )
#
#     def clear_selection(self):
#         for widget in self.ids.image_section.children:
#             if isinstance(widget, MyImage):
#                 widget.clear_selection()
#
#     def reload_image(self):
#         for widget in self.ids.image_section.children:
#             if isinstance(widget, MyImage) or isinstance(widget, MDSwiper):
#                 self.ids.image_section.remove_widget(widget)
#
#         self.image_original.truncate(0)
#         self.image_mask.truncate(0)
#         self.ids.add_image_button.disabled = False
#         self.ids.add_image_button.opacity = 1
#
#         while len(self.ids.edit_top_bar.right_action_items) != 0:
#             self.ids.edit_top_bar.right_action_items.remove(self.ids.edit_top_bar.right_action_items[-1])