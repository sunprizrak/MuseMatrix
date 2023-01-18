from kivy.cache import Cache
from kivy.network.urlrequest import UrlRequest
import json
from .models import Image
from .widget import MyImage


class OpenAIController:
    host_name = 'http://127.0.0.1:8000/'
    path_image_generation = host_name + 'openai/image_generation/'
    path_image_edit = host_name + 'openai/image_edit/'
    path_image_variation = host_name + 'openai/image_variation/'
    path_text_completion = host_name + 'openai/text_completion/'

    def image_generation(self, prompt, image_count, image_size, callback):
        # token = Cache.get('token', 'auth_token')
        token = '1be37f1ae2cbc7f90354ac42c8def1a29eaf21fb'

        UrlRequest(
            url=self.path_image_generation,
            method='GET',
            on_success=callback,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {token}",
            },
            req_body=json.dumps({'prompt': prompt, 'image_count': image_count, 'image_size': image_size}),
        )

    def image_edit(self, image, mask, prompt, image_count, image_size, callback):
        # token = Cache.get('token', 'auth_token')
        token = '1be37f1ae2cbc7f90354ac42c8def1a29eaf21fb'

        UrlRequest(
            url=self.path_image_edit,
            method='GET',
            on_success=callback,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {token}",
            },
            req_body=json.dumps({'image': image, 'mask': mask, 'prompt': prompt, 'image_count': image_count, 'image_size': image_size}),
        )

    def image_variation(self, image, image_count, image_size, callback):
        # token = Cache.get('token', 'auth_token')
        token = '1be37f1ae2cbc7f90354ac42c8def1a29eaf21fb'

        UrlRequest(
            url=self.path_image_variation,
            method='GET',
            on_success=callback,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {token}",
            },
            req_body=json.dumps({'image': image, 'image_count': image_count, 'image_size': image_size}),
        )

    def text_completion(self, prompt, callback):
        # token = Cache.get('token', 'auth_token')
        token = '1be37f1ae2cbc7f90354ac42c8def1a29eaf21fb'

        UrlRequest(
            url=self.path_text_completion,
            method='GET',
            on_success=callback,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {token}",
            },
            req_body=json.dumps({'prompt': prompt}),
        )


class ImageController:
    host_name = 'http://127.0.0.1:8000/'
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
                keep_ratio=False,
                allow_stretch=True,
                mipmap=True,
                img_id=image.id,
            )

            self.screen.core.root.ids.collection_screen.ids.selection_list.add_widget(img, index=len(self.object.images) - 1 if len(self.object.images) > 0 else 0)

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
                    img_id=image.id,
                )

                self.screen.core.root.ids.collection_screen.ids.selection_list.add_widget(img)

        UrlRequest(
            url=self.path_image,
            method='GET',
            on_success=callback,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {Cache.get('token', 'auth_token')}",
            },
        )

    def del_image(self, image_id, widget):

        def callback(request, response):
            self.object.delete_image(image_id=image_id)
            self.screen.core.root.ids.collection_screen.ids.selection_list.remove_widget(widget)
            self.screen.back(screen=self.screen.ids.full_image.back_screen)

        def callback_failure(request, response):
            print(response)

        UrlRequest(
            url=f'{self.path_image}{image_id}/',
            method='DELETE',
            on_success=callback,
            on_failure=callback_failure,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {Cache.get('token', 'auth_token')}",
            },
        )

    def del_images(self, images_id, widget_list):

        def callback(request, response):
            for image_id in images_id:
                self.object.delete_image(image_id=image_id)

            for widget in widget_list:
                self.screen.ids.selection_list.remove_widget(widget)
                self.screen.ids.selection_list.unselected_all()

        def callback_failure(request, response):
            print(response)

        UrlRequest(
            url=self.path_image_delete,
            method='DELETE',
            on_success=callback,
            on_failure=callback_failure,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {Cache.get('token', 'auth_token')}",
            },
            req_body=json.dumps(images_id),
        )







