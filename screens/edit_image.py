import base64
import io
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import NoTransition
from kivymd.uix.appbar import MDActionTopAppBarButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.transition import MDSlideTransition, MDSwapTransition
from widgets.EditImage import EditImage
from .layout import ImageScreen
from PIL import Image as PILImage


class EditImageScreen(ImageScreen):
    prompt = StringProperty()
    image = ObjectProperty()

    def __init__(self, **kwargs):
        super(EditImageScreen, self).__init__(**kwargs)
        self.image_original = io.BytesIO()
        self.image_mask = io.BytesIO()

    def on_pre_enter(self, *args):
        def _erase_percent(instance, value):
            self.image.erase_percent = int(value)

        self.ids.erase_percent.bind(value=_erase_percent)

    def add_image(self, path):
        self.image = EditImage(
            source=path,
            fit_mode='contain',
            mipmap=True,
        )

        if self.image.texture_size[0] == self.image.texture_size[1]:

            self.ids.add_image_button.disabled = True

            self.ids.bottom_buttons.buttons_disabled = False

            self.ids.image_box.add_widget(self.image, index=1)

            with PILImage.open(path) as img:
                img.save(self.image_original, format='png')
        else:
            text = 'The uploaded image must be a square image less than 4 MB in size'

            content = MDBoxLayout(
                MDLabel(
                    text=text,
                ),
                padding=[0, dp(10), 0, dp(10)],
            )

            self.app.show_dialog(title='Oops!', content=content)

    def edit_new_button(self, button):
        self.ids.input_prompt.text = ''
        self.image_count = 1
        self.ids.image_box.remove_widget(self.image)
        self.ids.add_image_button.disabled = False
        self.ids.bottom_buttons.buttons_disabled = True
        self.ids.carousel.clear_widgets()
        self.change_section(button=button)

    def change_section(self, button=None):
        if self.ids.screen_manager.current == 'edit_section':
            if isinstance(button, MDButton):
                if self.image.updated_texture:
                    self.ids.screen_manager.transition = MDSlideTransition()
                    self.ids.screen_manager.transition.direction = 'left'
                    self.ids.screen_manager.current = 'option_section'
                else:
                    text = 'You need to select an area to change'

                    content = MDBoxLayout(
                        MDLabel(
                            text=text,
                        ),
                        padding=[0, dp(10), 0, dp(10)],
                    )

                    self.app.show_dialog(title='Oops!', content=content)
            elif isinstance(button, MDActionTopAppBarButton):
                self.app.back(screen='main_screen')
        elif self.ids.screen_manager.current == 'option_section':
            if isinstance(button, MDButton):
                self.ids.screen_manager.transition = NoTransition()
                self.ids.screen_manager.current = 'completed_section'
            elif isinstance(button, MDActionTopAppBarButton):
                self.ids.screen_manager.transition = MDSlideTransition()
                self.ids.screen_manager.transition.direction = 'right'
                self.ids.screen_manager.current = 'edit_section'
        elif self.ids.screen_manager.current == 'completed_section':
            if isinstance(button, MDButton):
                self.ids.screen_manager.transition = NoTransition()
                self.ids.screen_manager.current = 'edit_section'

    def edit_image(self, button):
        def _on_success(request, response):
            if 'urls' in response:
                self.ids.edit_spin.active = False
                self.ids.option_section.disabled = False
                self.ids.screen_manager.transition = NoTransition()
                self.ids.screen_manager.current = 'completed_section'
                self.user_controller.user.coin = response.get('coin')
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
                self.ids.edit_spin.active = False
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
            self.ids.edit_spin.active = False
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

        def _on_error(request, error):
            _output_error(error)

        def _on_failure(request, response):
            _output_error(response)

        self.image_original.seek(0)

        if len(self.image_original.getvalue()) > 0:
            if all([self.prompt, self.image_count, self.image_size]):
                self.ids.option_section.disabled = True
                self.ids.edit_spin.active = True

                mask_img = self.image.get_mask_image()
                mask_img.save(self.image_mask, fmt='png')

                self.image_original.seek(0)
                png_image_original = self.image_original.getvalue()
                im_b64_image_original = base64.b64encode(png_image_original).decode('UTF-8')

                self.image_mask.seek(0)
                png_image_mask = self.image_mask.getvalue()
                im_b64_image_mask = base64.b64encode(png_image_mask).decode('UTF-8')

                self.openai_controller.image_edit(
                    image=im_b64_image_original,
                    mask=im_b64_image_mask,
                    prompt=self.prompt,
                    image_count=self.image_count,
                    image_size=self.image_size,
                    on_success=_on_success,
                    on_error=_on_error,
                    on_failure=_on_failure,
                )

    def clear_selection(self):
        self.image.clear_eraser()

    def reload_image(self):
        self.ids.image_box.remove_widget(self.image)
        self.image_original.truncate(0)
        self.image_mask.truncate(0)
        self.ids.add_image_button.disabled = False
        self.ids.bottom_buttons.buttons_disabled = True
        self.image_count = 1
        self.ids.input_prompt.text = ''