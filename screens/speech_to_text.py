from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty
from kivy.core.audio import SoundLoader
from controller.openai import OpenAIController
from controller.user import UserController
from .layout import BaseScreen


class SpeechToTextScreen(BaseScreen):
    sound = ObjectProperty(allownone=True)
    sound_pos = NumericProperty()

    def __init__(self, **kwargs):
        super(SpeechToTextScreen, self).__init__(**kwargs)
        self.openai_controller = OpenAIController()
        self.user_controller = UserController()
        self.event = None

    def add_sound(self, path, sound_name):
        self.ids.add_sound_button.disabled = True
        self.sound = SoundLoader.load(path)
        self.ids.sound.text = sound_name

        # button = MDButton(
        #     text='transcript',
        #     pos_hint={'center_x': .5, 'center_y': .5},
        #     font_size=sp(25),
        #     # md_bg_color=self.theme_cls.primary_color,
        #     on_release=lambda
        #         x: screen.transcript(),
        # )
        #
        # text_button = MDChipText(text='translate to english')
        #
        # chip = MDChip(
        #     pos_hint={'center_x': .5, 'center_y': .6},
        #     md_bg_color='grey',
        #     line_color="black",
        #     type='filter',
        #     selected_color='green',
        # )
        #
        # chip.add_widget(text_button)
        #
        # screen.ids.speech_layout.add_widget(button)
        # screen.ids.speech_layout.add_widget(chip)

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

        self.sound = None
        self.sound_pos = 0
        self.ids.sound.text = ''

        if self.event:
            self.event.cancel()

        remove_widgets = []

        # for widget in self.ids.speech_layout.children:
        #     if isinstance(widget, MDRaisedButton) or isinstance(widget, MDChip):
        #         remove_widgets.append(widget)

        # self.ids.speech_layout.clear_widgets(remove_widgets)
        # self.ids.add_sound_button.disabled = False
#
#     def transcript(self):
#         def _on_success(request, response):
#             self.ids.audio_transcript.text = response['text']
#             self.user_controller.user.coin = response['coin']
#             self.app.root.ids.main_screen.coin = self.user_controller.user.coin
#             self.ids.speech_top_bar.right_action_items = [['content-copy', lambda x: Clipboard.copy(self.ids.audio_transcript.text)]]
#
#         def _on_error(request, error):
#             print('error')
#             _output_error(error)
#
#         def _on_failure(request, response):
#             print('failure')
#             _output_error(response)
#
#         def _output_error(error):
#             print(error)
#             button = MDRaisedButton(
#                 text='transcript',
#                 pos_hint={'center_x': .5, 'center_y': .5},
#                 font_size=sp(25),
#                 md_bg_color=self.theme_cls.primary_color,
#                 on_release=lambda x: self.transcript()
#             )
#
#             text_button = MDChipText(text='translate to english')
#
#             chip = MDChip(
#                 pos_hint={'center_x': .5, 'center_y': .6},
#                 md_bg_color='grey',
#                 line_color="black",
#                 type='filter',
#                 selected_color='green',
#             )
#
#             chip.add_widget(text_button)
#
#             self.ids.speech_layout.add_widget(button)
#             self.ids.speech_layout.add_widget(chip)
#
#         def _on_finish(request):
#             self.ids.speech_spin.active = False
#
#         if self.sound:
#
#             remove_widgets = []
#             translate = False
#
#             for widget in self.ids.speech_layout.children:
#                 if isinstance(widget, MDRaisedButton) or isinstance(widget, MDChip):
#                     if isinstance(widget, MDChip):
#                         translate = widget.active
#                     remove_widgets.append(widget)
#
#             self.ids.speech_layout.clear_widgets(remove_widgets)
#
#             self.ids.speech_spin.active = True
#
#             length = int(self.sound.length / 60)
#
#             with open(self.sound.source, 'rb') as audio_file:
#                 base64_audio = base64.b64encode(audio_file.read()).decode('utf-8')
#                 name = audio_file.name.split('/')[-1]
#
#                 self.openai_controller.speech_to_text(
#                     audio_file=base64_audio,
#                     audio_name=name,
#                     audio_length=length,
#                     on_failure=_on_failure,
#                     on_error=_on_error,
#                     on_finish=_on_finish,
#                     on_success=_on_success,
#                     translate=translate,
#                 )