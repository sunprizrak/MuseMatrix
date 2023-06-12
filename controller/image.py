from models import Image
from widgets import MyImage
from kivy.network.urlrequest import UrlRequest
from settings import storage, host_name
import json


class ImageController:
    path_image = host_name + 'image/'
    path_image_delete = path_image + 'delete/'
    object = Image

    def __init__(self, screen):
        self.screen = screen

    def save_image(self, data_image):

        def callback(request, response):
            image = self.object(data_image=response)

            img = MyImage(
                sm=self.screen.core.root,
                source=image.source,
                fit_mode='contain',
                mipmap=True,
                img_id=image.id,
            )

            self.screen.core.root.ids.collection_screen.ids.selection_list.add_widget(img, index=len(self.object.images) - 1 if len(self.object.images) > 0 else 0)

            for index, widget in enumerate(reversed(self.screen.core.root.ids.collection_screen.ids.selection_list.children)):
                widget.instance_item.index = index

        def callback_failure(request, response):
            print(response)

        UrlRequest(
            url=self.path_image,
            method='POST',
            on_success=callback,
            on_failure=callback_failure,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {storage.get('auth_token').get('token')}",
            },
            req_body=json.dumps(data_image),
        )

    def get_image_list(self):

        def callback(request, response):
            for obj in response:
                self.object(data_image=obj)

            for index, image in enumerate(self.object.images):

                img = MyImage(
                    sm=self.screen.core.root,
                    source=image.source,
                    fit_mode='contain',
                    mipmap=True,
                    img_id=image.id,
                    index=index,
                )

                self.screen.core.root.ids.collection_screen.ids.selection_list.add_widget(img)

        UrlRequest(
            url=self.path_image,
            method='GET',
            on_success=callback,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {storage.get('auth_token').get('token')}",
            },
        )

    def del_image(self, image_id, widget_selection, widget_carousel):

        def callback(request, response):
            self.object.delete_image(image_id=image_id)
            self.screen.core.root.ids.collection_screen.ids.selection_list.remove_widget(widget_selection)
            self.screen.core.root.ids.open_img_screen.ids.carousel.remove_widget(widget_carousel)

            for index, widget in enumerate(reversed(self.screen.core.root.ids.collection_screen.ids.selection_list.children)):
                widget.instance_item.index = index

        def callback_failure(request, response):
            print(response)

        UrlRequest(
            url=f'{self.path_image}{image_id}/',
            method='DELETE',
            on_success=callback,
            on_failure=callback_failure,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {storage.get('auth_token').get('token')}",
            },
        )

    def del_images(self, images_id, widget_list):

        def callback(request, response):
            for image_id in images_id:
                self.object.delete_image(image_id=image_id)

            for widget in widget_list:
                self.screen.ids.selection_list.remove_widget(widget)
                self.screen.ids.selection_list.unselected_all()

            for index, widget in enumerate(reversed(self.screen.core.root.ids.collection_screen.ids.selection_list.children)):
                widget.instance_item.index = index

        def callback_failure(request, response):
            print(response)

        UrlRequest(
            url=self.path_image_delete,
            method='DELETE',
            on_success=callback,
            on_failure=callback_failure,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {storage.get('auth_token').get('token')}",
            },
            req_body=json.dumps(images_id),
        )

    def clear_image_list(self, widget_list):
        self.object.images.clear()
        widget_list.clear()