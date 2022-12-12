from kivy.cache import Cache
from kivy.network.urlrequest import UrlRequest
import json


class OpenAIController:
    host_name = 'http://127.0.0.1:8000/'
    path_get_image = host_name + 'api/openai/get_image'

    def get_image(self, prompt, image_count, image_size, callback):
        token = Cache.get('token', 'auth_token')
        UrlRequest(
            url=self.path_get_image,
            method='GET',
            on_success=callback,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {token}"
            },
            req_body=json.dumps({'prompt': prompt, 'image_count': image_count, 'image_size': image_size}),
        )








