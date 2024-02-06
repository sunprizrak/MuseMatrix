import base64
import io

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.swiper import MDSwiper
from kivymd.uix.transition import MDSwapTransition

from widgets.EditImage import EditImage
from widgets.MyCarousel import MyCarousel
from .layout import ImageScreen
from PIL import Image as PILImage


class EditImageScreen(ImageScreen):
    prompt = StringProperty()
    layout = ObjectProperty()
    image_edit_section = ObjectProperty()
    option_section = ObjectProperty()
    image = ObjectProperty()

    def __init__(self, **kwargs):
        super(EditImageScreen, self).__init__(**kwargs)
        self.image_original = io.BytesIO()
        self.image_mask = io.BytesIO()
        self.flag_section = False

    def on_pre_enter(self, *args):
        if not self.option_section:
            self.option_section = self.ids.option_section
            self.ids.layout.remove_widget(self.option_section)

        def _erase_percent(instance, value):
            self.image.erase_percent = int(value)

        self.ids.erase_percent.bind(value=_erase_percent)

    def add_image(self, path):
        self.image = EditImage(
            source=path,
            fit_mode='contain',
            mipmap=True,
            pos_hint={'center_x': .5, 'center_y': .5},
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

    def next_section(self):
        if self.image.updated_texture:
            self.image_edit_section = self.ids.image_edit_section
            self.ids.layout.remove_widget(self.image_edit_section)
            self.ids.layout.add_widget(self.option_section)
            self.flag_section = True
        else:
            text = 'You need to select an area to change'

            content = MDBoxLayout(
                MDLabel(
                    text=text,
                ),
                padding=[0, dp(10), 0, dp(10)],
            )

            self.app.show_dialog(title='Oops!', content=content)

    def back_section(self):
        self.ids.layout.remove_widget(self.option_section)
        self.ids.layout.add_widget(self.image_edit_section)
        self.flag_section = False

    def edit_image(self):
        def _on_success(request, response):
            if 'data' in response:
                self.ids.edit_spin.active = False
                self.user_controller.user.coin = response.get('coin')
                self.app.root.ids.main_screen.coin = self.user_controller.user.coin

                section_image = MDBoxLayout(
                    orientation='vertical',
                )

                self.ids.edit_layout.add_widget(section_image)

                top_button_wrap = MDBoxLayout(
                    orientation='horizontal',
                    adaptive_size=True,
                    padding=[dp(0), dp(10), dp(0), dp(10)],
                    spacing=dp(50),
                    pos_hint={'center_x': .5},
                )

                def _open_collection():
                    self.app.root.transition = MDSwapTransition()
                    self.app.root.current = 'collection_screen'

                collection_button = MDButton(
                    MDButtonIcon(icon='image-album'),
                    MDButtonText(
                        text='gallery',
                        theme_font_name="Custom",
                        font_name='Hacked',
                    ),
                    style='elevated',
                    radius=dp(10),
                    on_release=lambda x: _open_collection(),
                )

                top_button_wrap.add_widget(collection_button)

                def _return_section_option():
                    self.ids.edit_layout.remove_widget(section_image)
                    self.ids.edit_layout.add_widget(self.layout)
                    self.ids.input_prompt.text = ''
                    self.image_count = 1
                    self.layout.remove_widget(self.option_section)
                    self.layout.add_widget(self.image_edit_section)
                    self.ids.image_box.remove_widget(self.image)
                    self.ids.add_image_button.disabled = False
                    self.ids.bottom_buttons.buttons_disabled = True


                create_new_button = MDButton(
                    MDButtonIcon(icon='plus'),
                    MDButtonText(
                        text='Edit new',
                        theme_font_name="Custom",
                        font_name='Hacked',
                    ),
                    style='elevated',
                    radius=dp(10),
                    on_release=lambda x: _return_section_option(),
                )

                top_button_wrap.add_widget(create_new_button)

                section_image.add_widget(top_button_wrap)

                self.carousel = MyCarousel()

                for answer in response['data']:
                    url = answer.get('url')

                    image = FitImage(
                        source=url,
                        mipmap=True,
                        fit_mode='contain',
                    )

                    self.carousel.add_widget(image)

                section_image.add_widget(self.carousel)

                save_image_wrap = MDBoxLayout(
                    orientation='horizontal',
                    adaptive_size=True,
                    padding=[dp(30), dp(10), dp(30), dp(30)],
                    pos_hint={'center_x': .5},
                )

                save_image_button = MDButton(
                    MDButtonIcon(
                        icon='content-save',
                        icon_color_disabled='green',
                    ),
                    MDButtonText(
                        text='save image',
                        theme_font_name="Custom",
                        font_name='Hacked',
                        theme_text_color='Primary',

                    ),
                    pos_hint={'center_x': .5},
                    style='elevated',
                    radius=dp(10),
                    on_release=lambda x: self.save_image(widget=self.carousel.current_slide),
                )

                save_image_wrap.add_widget(save_image_button)
                section_image.add_widget(save_image_wrap)

                def _check_save(instance, value):
                    button = save_image_button
                    icon_obj = [widget for widget in button.children][1]
                    text_obj = [widget for widget in button.children][0]
                    if self.carousel.current_slide in self.carousel.saved_images:
                        button.disabled = True
                        icon_obj.icon = 'check-circle'
                        text_obj.text = 'saved'

                    else:
                        icon_obj.icon = 'content-save'
                        text_obj.text = 'save image'
                        button.disabled = False

                self.carousel.bind(saved_images=_check_save)
                self.carousel.bind(current_slide=_check_save)
            elif 'notice' in response:
                def _callback_one():
                    self.ids.edit_spin.active = False

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

                Clock.schedule_once(lambda dt: _callback_one(), 1)

                def _callback_two():
                    self.ids.edit_layout.add_widget(self.layout)

                Clock.schedule_once(lambda dt: _callback_two(), timeout=2)





            #     if len(response['data']) == 1:
            #         url = response['data'][0].get('url')
            #
            #         image = MyImage(
            #             source=url,
            #             fit_mode='contain',
            #             mipmap=True,
            #         )
            #
            #         self.ids.image_section.add_widget(image)
            #     elif len(response['data']) > 1:
            #         swiper = MDSwiper()
            #
            #         for el in response['data']:
            #             url = el.get('url')
            #
            #             item = MDSwiperItem()
            #
            #             image = MyImage(
            #                 source=url,
            #                 mipmap=True,
            #                 fit_mode='contain',
            #             )
            #
            #             item.add_widget(image)
            #             swiper.add_widget(item)
            #
            #         self.ids.image_section.add_widget(swiper)
            # elif 'notice' in response:
            #     self.ids.add_image_button.disabled = False
            #     self.ids.edit_top_bar.right_action_items = []
            #
            #     self.app.show_dialog()
            #     self.app.dialog.title = 'Notice!'
            #     self.app.dialog.text = response['notice']

        def _output_error(error):
            self.ids.edit_spin.active = False
            self.ids.add_image_button.disabled = False

            self.ids.edit_top_bar.right_action_items = []

            if type(error) is dict:
                if {'error'} & set(error):
                    self.app.show_dialog()
                    self.app.dialog.text = error.get('error')

        def _on_error(request, error):
            _output_error(error)

        def _on_failure(request, response):
            _output_error(response)

        self.image_original.seek(0)

        if len(self.image_original.getvalue()) > 0:
            if all([self.prompt, self.image_count]):  # self.image_size
                self.layout = self.ids.layout
                self.ids.edit_layout.remove_widget(self.layout)

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
                    image_size='1024x1024',
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