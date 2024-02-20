from kivymd.app import MDApp
from models import Image
from kivy.network.urlrequest import UrlRequest
from settings import host_name
import json

from widgets.MySelectionList import MySmartTile, MySmartTileImage


class ImageController:
    path_image = host_name + 'image/'
    path_image_delete = path_image + 'delete/'
    object = Image

    def __init__(self):
        self.app = MDApp.get_running_app()

    def save_image(self, **kwargs):

        UrlRequest(
            url=self.path_image,
            method='POST',
            on_success=kwargs.get('on_success'),
            on_failure=kwargs.get('on_failure'),
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
            },
            req_body=json.dumps(kwargs.get('data_image')),
        )

    def get_image_list(self):

        def _on_success(request, response):
            for obj in response:
                self.object(data_image=obj)

            screen = self.app.root.get_screen('collection_screen')

            for index, image in enumerate(self.object.images):

                smart_tile = MySmartTile()

                smart_tile_image = MySmartTileImage(
                    source=image.source,
                    img_id=image.id,
                    index=index,
                )
                smart_tile.add_widget(smart_tile_image)

                screen.ids.selection_list.add_widget(smart_tile)

        UrlRequest(
            url=self.path_image,
            method='GET',
            on_success=_on_success,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
            },
        )

    def del_image(self, **kwargs):

        UrlRequest(
            url=f"{self.path_image}{kwargs.get('image_id')}/",
            method='DELETE',
            on_success=kwargs.get('on_success'),
            on_failure=kwargs.get('on_failure'),
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
            },
        )

    def del_images(self, **kwargs):

        UrlRequest(
            url=self.path_image_delete,
            method='DELETE',
            on_success=kwargs.get('on_success'),
            on_failure=kwargs.get('on_failure'),
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
            },
            req_body=json.dumps(kwargs.get('images_id')),
        )

    def clear_image_list(self):
        self.object.images.clear()
        screen = self.app.root.get_screen('collection_screen')
        screen.ids.selection_list.children.clear()