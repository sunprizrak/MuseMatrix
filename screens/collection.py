from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu

from controller.image import ImageController
from .layout import BaseScreen


class CollectionScreen(BaseScreen):

    def __init__(self, **kwargs):
        super(CollectionScreen, self).__init__(**kwargs)
        self.image_controller = ImageController()
        menu_items = [
            {
                'text': 'Choose all',
                'on_release': lambda: (self.ids.selection_list.selected_all(), self.menu.dismiss()),
            }
        ]

        self.menu = MDDropdownMenu(
            items=menu_items,
        )

    def menu_callback(self, button):
        self.menu.caller = button
        self.menu.open()
    #
    # def delete_images(self, widget_list):
    #     images_id = [widget.children[1].img_id for widget in widget_list]
    #
    #     def del_images():
    #         self.image_controller.del_images(images_id=images_id, widget_list=widget_list)
    #         self.app.dialog.dismiss()
    #
    #     button = MDFillRoundFlatButton(
    #         text="Delete",
    #         on_release=lambda x: del_images(),
    #     )
    #
    #     self.app.show_dialog(button=button)
    #     self.app.dialog.title = 'Delete'
    #     self.app.dialog.text = 'Are you sure you want to delete?'