from kivy.properties import StringProperty
from kivy.uix.screenmanager import FallOutTransition

from controller.image import ImageController
from controller.user import UserController
from .layout import BaseScreen


class OpenImageScreen(BaseScreen):
    back_screen = StringProperty()

    def __init__(self, **kwargs):
        super(OpenImageScreen, self).__init__(**kwargs)
        self.user_controller = UserController()
        self.image_controller = ImageController()
#
#     def on_pre_enter(self, *args):
#         screen = self.app.root.get_screen(self.back_screen)
#
#         if self.back_screen == 'collection_screen':
#             images = [el.instance_item for el in screen.ids.selection_list.children]
#         else:
#             for widget in screen.ids.image_section.children:
#                 if isinstance(widget, MyImage):
#                     images = [widget]
#                 elif isinstance(widget, MDSwiper):
#                     images = [el.children[0].children[0] for el in widget.children[0].children]
#
#         images.reverse()
#
#         for obj in images:
#
#             image = Image(
#                 mipmap=True,
#                 texture=obj.texture,
#                 fit_mode='contain',
#                 pos_hint={'center_y': .5}
#             )
#
#             if self.back_screen == 'collection_screen':
#                 image.img_id = obj.img_id
#                 image.pre_parent = obj.parent
#
#             self.ids.carousel.add_widget(image)
#
#     def on_leave(self, *args):
#         self.ids.carousel.clear_widgets()
#
    def back(self, screen):
        # if len(self.ids.app_bar.right_action_items) > 1:
        #     self.ids.app_bar.right_action_items.remove(self.ids.app_bar.right_action_items[0])
        self.app.root.transition = FallOutTransition()
        self.app.root.current = screen
#
#     def download(self, img):
#
#         def save_image():
#             image = CoreImage(img.texture)
#
#             if platform == 'android':
#                 private_path = join(self.app.ss.get_cache_dir(), f'{str(uuid.uuid4())}.png')
#
#                 image.save(private_path)
#
#                 if exists(private_path):
#                     self.app.ss.copy_to_shared(private_path)
#
#             if self.back_screen in ('create_image_screen', 'edit_image_screen', 'variable_image_screen'):
#                 data = io.BytesIO()
#                 image.save(data, fmt='png')
#                 png_bytes = data.read()
#                 im_b64 = base64.b64encode(png_bytes).decode('utf-8')
#
#                 data_image = {
#                     'user': self.user_controller.user.id,
#                     'source': im_b64,
#                 }
#
#                 screen = self.app.root.get_screen(self.back_screen)
#
#                 if screen.name != 'variable_image_screen':
#                     data_image['description'] = screen.prompt
#
#                 self.image_controller.save_image(data_image=data_image)
#
#             toast(text='image saved')
#             self.app.dialog.dismiss()
#
#         button = MDFillRoundFlatButton(
#             text="Save",
#             on_release=lambda x: save_image(),
#         )
#
#         self.app.show_dialog(button=button)
#         self.app.dialog.title = 'Save image'
#         self.app.dialog.text = 'Do you want to save the picture?'
#
#     def delete(self, img_id, widget_selection):
#
#         def del_image():
#             self.image_controller.del_image(image_id=img_id, widget_selection=widget_selection, widget_carousel=self.ids.carousel.current_slide)
#             self.app.dialog.dismiss()
#
#         button = MDFillRoundFlatButton(
#             text="Delete",
#             on_release=lambda x: del_image(),
#         )
#
#         self.app.show_dialog(button=button)
#         self.app.dialog.title = 'Delete'
#         self.app.dialog.text = 'Are you sure you want to delete??'