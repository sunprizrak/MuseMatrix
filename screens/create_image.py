from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import NoTransition
from kivy.uix.widget import Widget
from kivymd.uix.appbar import MDActionTopAppBarButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.transition import MDSwapTransition, MDSlideTransition

from widgets.MyCarousel import MyCarousel
from .layout import ImageScreen


class CreateImageScreen(ImageScreen):
    prompt = StringProperty()
    dall_model = StringProperty()

    def __init__(self, **kwargs):
        super(CreateImageScreen, self).__init__(**kwargs)

    def segment_dall_model(self, model):
        if self.dall_model != model:
            self.image_size = ''
            self.image_count = 1
            self.dall_model = model

            for button in self.ids.seg_size.children:
                if isinstance(button, MDButton):
                    button.theme_bg_color = 'Primary'
                    button.children[0].theme_text_color = 'Primary'
                    button.parent.current = Widget()

    def edit_new_button(self):
        self.ids.input_prompt.text = ''
        self.image_count = 1
        self.ids.carousel.clear_widgets()
        self.ids.screen_manager.transition = NoTransition()
        self.ids.screen_manager.current = 'option_section'

    def generate(self):
        def _on_success(request, response):
            if 'urls' in response:
                self.ids.option_section.disabled = False
                self.ids.create_spin.active = False
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
                self.ids.create_spin.active = False
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
            self.ids.create_spin.active = False
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

        def _on_failure(request, response):
            _output_error(response)

        def _on_error(request, error):
            _output_error(error)

        if all([self.dall_model, self.prompt, self.image_count, self.image_size]):
            self.ids.option_section.disabled = True
            self.ids.create_spin.active = True

            self.openai_controller.image_generation(
                dall_model=self.dall_model,
                prompt=self.prompt,
                image_count=self.image_count,
                image_size=self.image_size,
                on_success=_on_success,
                on_error=_on_error,
                on_failure=_on_failure,
            )