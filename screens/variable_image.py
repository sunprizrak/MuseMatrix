import base64
from kivy.metrics import dp
from kivy.uix.screenmanager import NoTransition
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage
from PIL import Image as PILImage
from kivymd.uix.label import MDLabel
from .layout import ImageScreen
import io


class VariableImageScreen(ImageScreen):
    image = io.BytesIO()

    def __init__(self, **kwargs):
        super(VariableImageScreen, self).__init__(**kwargs)

    def add_image(self, path):
        image = FitImage(
            source=path,
            fit_mode='contain',
            mipmap=True,
        )

        if image.texture_size[0] == image.texture_size[1]:

            self.ids.add_image_button.disabled = True

            self.ids.image_box.add_widget(image, index=0)
            self.ids.img_reload.disabled = False

            with PILImage.open(path) as img:
                img.save(self.image, format='png')
        else:
            text = 'The uploaded image must be a square image less than 4 MB in size'

            content = MDBoxLayout(
                MDLabel(
                    text=text,
                ),
                padding=[0, dp(10), 0, dp(10)],
            )

            self.app.show_dialog(title='Oops!', content=content)

    def reload_image(self):
        for widget in self.ids.image_box.children:
            if isinstance(widget, FitImage):
                self.ids.image_box.remove_widget(widget)
                break

        self.image.truncate(0)
        self.ids.add_image_button.disabled = False
        self.ids.img_reload.disabled = True

    def variable_new_button(self):
        self.image_count = 1
        self.reload_image()
        self.ids.carousel.clear_widgets()
        self.ids.screen_manager.transition = NoTransition()
        self.ids.screen_manager.current = 'option_section'

    def generate(self):

        def _on_success(request, response):
            if 'urls' in response:
                self.ids.variable_spin.active = False
                self.ids.option_section.disabled = False
                self.ids.screen_manager.transition = NoTransition()
                self.ids.screen_manager.current = 'completed_section'
                self.user_controller.user.coin = response['coin']
                self.app.root.ids.main_screen.coin = self.user_controller.user.coin

                for image_url in response['urls']:
                    url = image_url

                    image = FitImage(
                        source=url,
                        mipmap=True,
                        fit_mode='contain',
                    )

                    self.ids.carousel.add_widget(image)
            elif 'notice' in response:
                self.ids.variable_spin.active = False
                self.ids.option_section.disabled = False

                content = MDBoxLayout(
                    MDLabel(
                        text=response['notice'],
                    ),
                    padding=[0, dp(10), 0, dp(10)],
                )

                self.app.show_dialog(
                    title='Oops!',
                    content=content,
                )

        def _output_error(error):
            self.ids.variable_spin.active = False
            self.ids.option_section.disabled = False

            error_text = 'error'

            if type(error) is dict:
                if {'error'} & set(error):
                    error_text = error.get('error')
            elif type(error) is ConnectionRefusedError:
                error_text = error.strerror

            content = MDBoxLayout(
                MDLabel(
                    text=error_text,
                ),
                padding=[0, dp(10), 0, dp(10)],
            )

            self.app.show_dialog(
                title='Oops!',
                content=content,
            )

            if type(error) is dict:
                if {'error'} & set(error):
                    self.app.show_dialog()
                    self.app.dialog.text = error.get('error')

        def _on_error(request, error):
            _output_error(error)

        def _on_failure(request, response):
            _output_error(response)

        self.image.seek(0)
        if len(self.image.getvalue()) > 0:
            if all([self.image_count, self.image_size]):
                self.ids.option_section.disabled = True
                self.ids.variable_spin.active = True

                self.image.seek(0)
                image_png = self.image.getvalue()
                im_b64_image = base64.b64encode(image_png).decode('UTF-8')

                self.openai_controller.image_variation(
                    image=im_b64_image,
                    image_count=self.image_count,
                    image_size=self.image_size,
                    on_success=_on_success,
                    on_error=_on_error,
                    on_failure=_on_failure,
                )
            else:
                content = MDBoxLayout(
                    MDLabel(
                        text='You need to select all parameters for generation',
                    ),
                    padding=[0, dp(10), 0, dp(10)],
                )

                self.app.show_dialog(
                    title='Oops!',
                    content=content,
                )
        else:
            content = MDBoxLayout(
                MDLabel(
                    text='Уou need to upload images',
                ),
                padding=[0, dp(10), 0, dp(10)],
            )

            self.app.show_dialog(
                title='Oops!',
                content=content,
            )
