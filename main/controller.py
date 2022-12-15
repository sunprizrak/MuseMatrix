from kivy.cache import Cache
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.fitimage import FitImage
from .models import Image
import json


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
            print(response)

        UrlRequest(
            url=self.path_image,
            method='POST',
            on_success=callback,
            req_headers={
                'Authorization': f"Token {Cache.get('token', 'auth_token')}",
                'Content-type': 'multipart/form-data',
            },
            req_body=json.dumps(data_image),
        )

    def get_image_list(self):

        def callback(request, response):
            for obj in response:
                self.object(data_image=obj)

            for image in self.object.images:

                img = FitImage(
                    source=image.source,
                )

                self.screen.core.root.ids.main_screen.ids.collection.add_widget(img)

        UrlRequest(
            url=self.path_image,
            method='GET',
            on_success=callback,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {Cache.get('token', 'auth_token')}",
            },
        )








