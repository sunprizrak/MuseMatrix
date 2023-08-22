from kivy.network.urlrequest import UrlRequest
import json
from settings import host_name
from kivymd.app import MDApp


class OpenAIController:
    path_image_generation = host_name + 'openai/image_generation/'
    path_image_edit = host_name + 'openai/image_edit/'
    path_image_variation = host_name + 'openai/image_variation/'
    path_chat_completion = host_name + 'openai/chat_completion/'
    path_speech_to_text = host_name + 'openai/speech_to_text/'

    def __init__(self):
        self.app = MDApp.get_running_app()

    def image_generation(self, *args, **kwargs):

        UrlRequest(
            url=self.path_image_generation,
            method='GET',
            on_success=kwargs.get('on_success'),
            on_error=kwargs.get('on_error'),
            on_failure=kwargs.get('on_failure'),
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
            },
            req_body=json.dumps({
                'prompt': kwargs.get('prompt'),
                'image_count': kwargs.get('image_count'),
                'image_size': kwargs.get('image_size'),
            }),
        )

    def image_edit(self, *args, **kwargs):

        UrlRequest(
            url=self.path_image_edit,
            method='GET',
            on_success=kwargs.get('on_success'),
            on_error=kwargs.get('on_error'),
            on_failure=kwargs.get('on_failure'),
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
            },
            req_body=json.dumps({
                'image': kwargs.get('image'),
                'mask': kwargs.get('mask'),
                'prompt': kwargs.get('prompt'),
                'image_count': kwargs.get('image_count'),
                'image_size': kwargs.get('image_size'),
            }),
        )

    def image_variation(self, *args, **kwargs):

        UrlRequest(
            url=self.path_image_variation,
            method='GET',
            on_success=kwargs.get('on_success'),
            on_error=kwargs.get('on_error'),
            on_failure=kwargs.get('on_failure'),
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
            },
            req_body=json.dumps({'image': kwargs.get('image'), 'image_count': kwargs.get('image_count'), 'image_size': kwargs.get('image_size')}),
        )

    def chat_completion(self, *args, **kwargs):

        UrlRequest(
            url=self.path_chat_completion,
            method='GET',
            on_success=kwargs.get('on_success'),
            on_error=kwargs.get('on_error'),
            on_failure=kwargs.get('on_failure'),
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
            },
            req_body=json.dumps({'prompt': kwargs.get('prompt')}),
        )

    def speech_to_text(self, *args, **kwargs):

        UrlRequest(
            url=self.path_speech_to_text,
            method='GET',
            on_success=kwargs.get('on_success'),
            on_failure=kwargs.get('on_failure'),
            on_error=kwargs.get('on_error'),
            on_finish=kwargs.get('on_finish'),
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {self.app.storage.get('auth_token').get('token')}",
            },
            req_body=json.dumps({'audio_file': kwargs.get('audio_file'),
                                 'audio_name': kwargs.get('audio_name'),
                                 'audio_length': kwargs.get('audio_length'),
                                 'translate': kwargs.get('translate'),
                                 }),
        )
