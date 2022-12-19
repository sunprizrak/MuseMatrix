from kivy.cache import Cache
from kivy.network.urlrequest import UrlRequest
import json
from .models import Image
from .widget import MyImage


class OpenAIController:
    host_name = 'http://127.0.0.1:8000/'
    path_get_image = host_name + 'openai/get_image/'

    def get_image(self, prompt, image_count, image_size, callback):
        # token = Cache.get('token', 'auth_token')
        token = '1be37f1ae2cbc7f90354ac42c8def1a29eaf21fb'

        UrlRequest(
            url=self.path_get_image,
            method='GET',
            on_success=callback,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {token}",
            },
            req_body=json.dumps({'prompt': prompt, 'image_count': image_count, 'image_size': image_size}),
        )


class ImageController:
    host_name = 'http://127.0.0.1:8000/'
    path_image = host_name + 'image/'
    object = Image

    def __init__(self, screen):
        self.screen = screen

    def save_image(self, data_image):

        def callback(request, response):
            image = self.object(data_image=response)

            img = MyImage(
                sm=self.screen.core.root,
                source=image.source,
                keep_ratio=False,
                allow_stretch=True,
                mipmap=True,
            )

            self.screen.core.root.ids.main_screen.ids.selection_list.add_widget(img, index=len(self.object.images) - 1 if len(self.object.images) > 0 else 0)

        def callback_failure(request, response):
            print(response)

        UrlRequest(
            url=self.path_image,
            method='POST',
            on_success=callback,
            on_failure=callback_failure,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {Cache.get('token', 'auth_token')}",
            },
            req_body=json.dumps(data_image),
        )

    def get_image_list(self):

        def callback(request, response):
            for obj in response:
                self.object(data_image=obj)

            for image in self.object.images:

                img = MyImage(
                    sm=self.screen.core.root,
                    source=image.source,
                    keep_ratio=False,
                    allow_stretch=True,
                    mipmap=True,
                )

                self.screen.core.root.ids.main_screen.ids.selection_list.add_widget(img)

        UrlRequest(
            url=self.path_image,
            method='GET',
            on_success=callback,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {Cache.get('token', 'auth_token')}",
            },
        )








