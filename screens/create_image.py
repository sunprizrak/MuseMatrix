from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.carousel import Carousel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.label import MDLabel

from widgets import MyImage
from .layout import ImageScreen


class CreateImageScreen(ImageScreen):
    prompt = StringProperty()
    dall_model = StringProperty()
    section_option = ObjectProperty()

    def __init__(self, **kwargs):
        super(CreateImageScreen, self).__init__(**kwargs)

    def segment_dall_model(self):
        self.image_size = ''
        self.image_count = 1

        for button in self.ids.seg_size.children[0].children:
            button.active = False

    def generate(self):
        def _on_success(request, response):
            if 'data' in response:
                self.ids.create_spin.active = False
                self.user_controller.user.coin = response.get('coin')
                self.app.root.ids.main_screen.coin = self.user_controller.user.coin

                section_image = MDBoxLayout(
                    orientation='vertical',
                )

                self.ids.create_layout.add_widget(section_image)

                create_new_wrap = MDBoxLayout(
                    orientation='horizontal',
                    adaptive_size=True,
                    padding=[dp(0), dp(10), dp(0), dp(10)],
                    pos_hint={'center_x': .75},
                )

                def _return_section_option():
                    self.ids.create_layout.remove_widget(section_image)
                    self.ids.create_layout.add_widget(self.section_option)

                create_new_button = MDButton(
                    MDButtonIcon(icon='plus'),
                    MDButtonText(
                        text='Create new',
                        theme_font_name="Custom",
                        font_name='Hacked',
                    ),
                    style='elevated',
                    on_release=lambda x: _return_section_option(),
                )

                create_new_wrap.add_widget(create_new_button)

                section_image.add_widget(create_new_wrap)

                if len(response['data']) == 1:
                    url = response['data'][0].get('url')

                    image = MyImage(
                        source=url,
                        fit_mode='contain',
                        mipmap=True,
                    )

                    section_image.add_widget(image)
                elif len(response['data']) > 1:
                    carousel = Carousel()

                    for index, el in enumerate(response['data']):
                        url = el.get('url')

                        image = MyImage(
                            source=url,
                            mipmap=True,
                            fit_mode='contain',
                            index=index,
                        )

                        carousel.add_widget(image)

                    section_image.add_widget(carousel)

                save_image_wrap = MDBoxLayout(
                    orientation='horizontal',
                    adaptive_size=True,
                    padding=[dp(30), dp(10), dp(30), dp(30)],
                    pos_hint={'center_x': .5},
                )

                save_image_button = MDButton(
                    MDButtonIcon(icon='content-save'),
                    MDButtonText(
                        text='Save image',
                        theme_font_name="Custom",
                        font_name='Hacked',
                    ),
                    style='elevated',
                )

                save_image_wrap.add_widget(save_image_button)

                section_image.add_widget(save_image_wrap)

            elif 'notice' in response:
                def _callback_one():
                    self.ids.create_spin.active = False

                    content = MDBoxLayout(
                        MDLabel(
                            text=response['notice'],
                            padding=[0, dp(10), 0, 0],
                        ),
                    )

                    self.app.show_dialog(
                        title='Oops!',
                        content=content,
                    )

                Clock.schedule_once(lambda dt: _callback_one(), 1)

                def _callback_two():
                    self.ids.create_layout.add_widget(self.section_option)

                Clock.schedule_once(lambda dt: _callback_two(), timeout=2)

        def _output_error(error):
            def _callback_one():
                self.ids.create_spin.active = False

                error_text = 'error'

                if type(error) is dict:
                    if {'error'} & set(error):
                        error_text = error.get['error']
                elif type(error) is ConnectionRefusedError:
                    error_text = error.strerror

                content = MDBoxLayout(
                    MDLabel(
                        text=error_text,
                        padding=[0, dp(10), 0, 0],
                    ),
                )

                self.app.show_dialog(
                    title='Oops!',
                    content=content,
                )

            Clock.schedule_once(lambda dt: _callback_one(), 1)

            def _callback_two():
                self.ids.create_layout.add_widget(self.section_option)

            Clock.schedule_once(lambda dt: _callback_two(), timeout=2)

        def _on_failure(request, response):
            _output_error(response)

        def _on_error(request, error):
            _output_error(error)

        if all([self.dall_model, self.prompt, self.image_count, self.image_size]):

            self.ids.create_spin.active = True

            self.section_option = self.ids.section_option

            self.ids.create_layout.remove_widget(self.ids.section_option)

            self.openai_controller.image_generation(
                dall_model=self.dall_model,
                prompt=self.prompt,
                image_count=self.image_count,
                image_size=self.image_size,
                on_success=_on_success,
                on_error=_on_error,
                on_failure=_on_failure,
            )