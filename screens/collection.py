from copy import copy
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
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
                'theme_font_name': 'Custom',
                'font_name': 'Hacked',
                'on_release': lambda: (self.ids.selection_list.selected_all(), self.menu.dismiss()),
            }
        ]

        self.menu = MDDropdownMenu(
            items=menu_items,
            position="center"
        )

    def menu_callback(self, button):
        self.menu.caller = button
        self.menu.open()

    def delete_images(self, widget_list):
        images_id = [widget.image.img_id for widget in widget_list]

        def _del_images():
            def _on_success(request, response):
                for image_id in images_id:
                    self.image_controller.object.delete_image(image_id=image_id)

                for widget in copy(widget_list):
                    self.ids.selection_list.unselected_all()
                    self.ids.selection_list.remove_widget(widget)

                for index, smart_tile in enumerate(reversed(self.ids.selection_list.children)):
                    smart_tile.image.index = index

            def _on_failure(request, response):
                print(response)

            self.image_controller.del_images(
                images_id=images_id,
                on_success=_on_success,
                on_failure=_on_failure,
            )

            self.app.dialog.dismiss()

        button = MDButton(
            MDButtonText(
                text='delete',
                theme_text_color="Custom",
                text_color='white',
                theme_font_name="Custom",
                font_name='Hacked',
            ),
            style='filled',
            theme_bg_color='Custom',
            md_bg_color='red',
            on_release=lambda x: _del_images(),
        )

        content = MDBoxLayout(
            MDLabel(
                text='Are you sure you want to delete?',
            ),
            padding=[0, dp(10), 0, dp(10)],
        )

        self.app.show_dialog(
            title='Delete images',
            button=button,
            content=content,
        )