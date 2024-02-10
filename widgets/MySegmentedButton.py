from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton


class MySegmentedButton(MDBoxLayout):
    current = ObjectProperty()

    def __init__(self, **kwargs):
        super(MySegmentedButton, self).__init__(**kwargs)
        self.bind(current=lambda inst, val: self.__change_current_color(instance=inst, value=val))

    def __change_current_color(self, instance, value):
        if isinstance(value, MDButton):
            for button in self.children:
                if isinstance(button, MDButton):
                    button.theme_bg_color = 'Primary'
                    button.children[0].theme_text_color = 'Primary'

            value.theme_bg_color = 'Custom'
            value.md_bg_color = 'green'
            value.children[0].theme_text_color = 'Custom'
            value.children[0].text_color = 'white'