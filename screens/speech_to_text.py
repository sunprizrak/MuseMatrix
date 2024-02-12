import base64
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.properties import ObjectProperty, NumericProperty
from kivy.core.audio import SoundLoader
from kivy.uix.checkbox import CheckBox
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from controller.openai import OpenAIController
from controller.user import UserController
from .layout import BaseScreen
from kivy.core.clipboard import Clipboard
from kivy.utils import platform

if platform == 'android':
    from kivymd.toast import toast


class SpeechToTextScreen(BaseScreen):
    sound = ObjectProperty(allownone=True)
    sound_pos = NumericProperty()

    def __init__(self, **kwargs):
        super(SpeechToTextScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.user_controller = UserController()
        self.event = None

    def __add_option(self):
        label = MDLabel(
            text='translate the translation into English?',
            theme_font_name='Custom',
            font_name='Hacked',
            adaptive_size=True,
            pos_hint={'center_x': .5, 'center_y': .7},
        )

        check_box = CheckBox(
            pos_hint={'center_x': .5, 'center_y': .6},
            size_hint=(None, None),
            size=(dp(26), dp(26)),
        )
        self.ids.speech_layout.add_widget(label)
        self.ids.speech_layout.add_widget(check_box)

        button = MDButton(
            MDButtonText(
                text='transcript',
                pos_hint={'center_x': .5},
                theme_font_name='Custom',
                font_name='Hacked',
                font_style='Display',
                role='small',
            ),
            style='elevated',
            theme_width='Custom',
            size_hint_x=1,
            radius=dp(0),
            pos_hint={'bottom': 1},
            on_release=lambda x: self.transcript(),
        )

        self.ids.speech_layout.add_widget(button)

    def add_sound(self, path, sound_name):
        self.ids.add_sound_button.disabled = True
        self.sound = SoundLoader.load(path)
        self.ids.sound.text = sound_name
        self.__add_option()

    def sound_play(self):
        if self.sound:
            if self.sound.state == 'play':
                self.sound_pos = self.sound.get_pos()
                self.sound.stop()
                self.ids.sound_option.icon_play = 'play'
                self.event.cancel()
            elif self.sound.state == 'stop':
                if self.sound_pos:
                    self.sound.seek(self.sound_pos)
                self.sound.play()
                self.ids.sound_option.icon_play = 'pause'

                end_sound = self.sound.length - self.sound.get_pos() + 1

                def _callback(args, **kwargs):
                    self.ids.sound_option.icon_play = 'play'

                self.event = Clock.schedule_once(callback=_callback, timeout=end_sound)
                self.event()

    def sound_stop(self):
        if self.sound.state == 'play':
            self.ids.sound_option.icon_play = 'play'

        self.sound.stop()
        self.sound_pos = 0

        if self.event:
            self.event.cancel()

    def delete_sound(self):
        if self.sound.state == 'play':
            self.sound.stop()

        if self.ids.audio_transcript.text:
            self.ids.audio_transcript.text = ''

        if self.ids.speech_spin.active is True:
            self.ids.speech_spin.active = False

        self.ids.bottom_buttons.disabled = True

        self.sound = None
        self.sound_pos = 0
        self.ids.sound.text = ''

        if self.event:
            self.event.cancel()

        remove_widgets = []

        for widget in self.ids.speech_layout.children:
            if isinstance(widget, MDLabel) or isinstance(widget, MDButton) or isinstance(widget, CheckBox):
                remove_widgets.append(widget)

        self.ids.speech_layout.clear_widgets(remove_widgets)

        self.ids.add_sound_button.disabled = False

    def transcript(self):
        def _on_success(request, response):
            if 'text' in response:
                self.ids.audio_transcript.text = response.get('text')
                self.user_controller.user.coin = response.get('coin')
                self.app.root.ids.main_screen.coin = self.user_controller.user.coin
                self.ids.bottom_buttons.disabled = False
            elif 'notice' in response:
                self.__add_option()

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

        def __output_error(error):
            self.__add_option()

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
            __output_error(error)

        def _on_failure(request, response):
            __output_error(response)

        def _on_finish(request):
            self.ids.speech_spin.active = False

        if self.sound:

            remove_widgets = []
            translate = False

            for widget in self.ids.speech_layout.children:
                if isinstance(widget, MDLabel) or isinstance(widget, CheckBox) or isinstance(widget, MDButton):
                    if isinstance(widget, CheckBox):
                        translate = widget.active
                    remove_widgets.append(widget)

            self.ids.speech_layout.clear_widgets(remove_widgets)

            self.ids.speech_spin.active = True

            length = int(self.sound.length / 60)

            with open(self.sound.source, 'rb') as audio_file:
                base64_audio = base64.b64encode(audio_file.read()).decode('UTF-8')
                name = audio_file.name.split('/')[-1]

                self.openai_controller.speech_to_text(
                    audio_file=base64_audio,
                    audio_name=name,
                    audio_length=length,
                    on_failure=_on_failure,
                    on_error=_on_error,
                    on_finish=_on_finish,
                    on_success=_on_success,
                    translate=translate,
                )

    def copy_to_buffer(self):
        Clipboard.copy(self.ids.audio_transcript.text)

        if platform == 'android':
            toast(
                text="Text copied to clipboard",
                length_long=True,
                gravity=40,
                y=self.top,
                x=0,
            )