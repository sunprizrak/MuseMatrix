from copy import copy
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ObjectProperty, ListProperty, NumericProperty
from kivy.uix.screenmanager import RiseInTransition
from kivymd.app import MDApp
from kivymd.uix.appbar import MDActionTopAppBarButton
from kivymd.uix.behaviors import TouchBehavior, RectangularRippleBehavior
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.imagelist import MDSmartTile, MDSmartTileImage, MDSmartTileOverlayContainer
from kivymd.uix.selectioncontrol import MDCheckbox


class MySmartTileImage(MDSmartTileImage):
    img_id = NumericProperty()
    index = NumericProperty()

    def __init__(self, **kwargs):
        super(MySmartTileImage, self).__init__(**kwargs)
        self.ripple_effect = False


class MySmartTileOverlayContainer(MDSmartTileOverlayContainer):
    def __init__(self, **kwargs):
        super(MySmartTileOverlayContainer, self).__init__(**kwargs)

    @property
    def check_box(self):
        data_list = [widget for widget in self.children if isinstance(widget, MDCheckbox)]
        if data_list:
            check_box = data_list[0]
            return check_box
        else:
            return

    def on_touch_down(self, touch):
        if self.check_box and self.check_box.collide_point(*touch.pos):
            self.check_box.active = False if self.check_box.active else True
            return True

        return super(MySmartTileOverlayContainer, self).on_touch_down(touch)

    def add_check_box(self):
        def _on_active_checkbox(obj, value):
            image = self.parent.image
            image.size_hint = (None, None)
            image.size = [image.size[0] - 30, image.size[1] - 30] if self.check_box.active else self.parent.size
            image.pos_hint = {'center_x': .5, 'center_y': .5}

            app = MDApp.get_running_app()
            screen = app.root.get_screen(app.root.current)

            if self.check_box.active:
                if self.parent not in self.parent.parent.selected_items:
                    self.parent.parent.selected_items.append(self.parent)
            else:
                if self.parent in self.parent.parent.selected_items:
                    self.parent.parent.selected_items.remove(self.parent)

            if len(self.parent.parent.selected_items) == 0:
                for widget in self.parent.parent.children:
                    widget.container.delete_check_box()

                for button in copy(screen.ids.left_button.children):
                    if isinstance(button, MDActionTopAppBarButton):
                        screen.ids.left_button.remove_widget(button)

                if self.parent.parent.back_button:
                    screen.ids.left_button.add_widget(self.parent.parent.back_button)

                screen.ids.button_delete.disabled = True
                screen.ids.button_delete.theme_icon_color = 'Custom'
                screen.ids.button_delete.icon_color = screen.md_bg_color

            screen.ids.collection_app_bar_title.text = str(len(self.parent.parent.selected_items)) if len(self.parent.parent.selected_items) > 0 else ' '

        check_box = MDCheckbox(
            checkbox_icon_normal='checkbox-blank-circle-outline',
            checkbox_icon_down='checkbox-marked-circle',
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={'y': .7},
        )

        check_box.bind(active=_on_active_checkbox)

        self.add_widget(check_box)

    def delete_check_box(self):
        if self.check_box:
            def _callback(dt):
                self.remove_widget(self.check_box)

            Clock.schedule_once(callback=_callback)


class MySmartTile(TouchBehavior, RectangularRippleBehavior, MDSmartTile):
    def __init__(self, **kwargs):
        super(MySmartTile, self).__init__(**kwargs)
        self.md_bg_color = self.theme_cls.tertiaryColor
        self.__long_touch_event = True
        self.__open_image = True

    @property
    def image(self):
        data_list = [widget for widget in self.children if isinstance(widget, MySmartTileImage)]
        if data_list:
            image = data_list[0]
            return image
        else:
            return

    @property
    def container(self):
        data_list = [widget for widget in self.children if isinstance(widget, MySmartTileOverlayContainer)]
        if data_list:
            container = data_list[0]
            return container
        else:
            return

    def select_image(self):
        if len(self.parent.selected_items) == 0:
            for widget in self.parent.children:
                if not widget.container:
                    widget.add_widget(MySmartTileOverlayContainer())

                if not widget.container.check_box:
                    widget.container.add_check_box()

                if widget is self:
                    widget.container.check_box.active = True

            app = MDApp.get_running_app()
            screen = app.root.get_screen(app.root.current)

            for button in screen.ids.left_button.children:
                if isinstance(button, MDActionTopAppBarButton):
                    self.parent.back_button = button
                    screen.ids.left_button.remove_widget(button)

            un_button = MDActionTopAppBarButton(
                icon='close-thick',
                theme_icon_color='Custom',
                icon_color=self.theme_cls.primaryColor,
                ripple_effect=False,
                focus_behavior=False,
                on_release=lambda x: self.parent.unselected_all()
            )

            screen.ids.left_button.add_widget(un_button)

            screen.ids.button_delete.disabled = False
            screen.ids.button_delete.icon_color = self.theme_cls.primaryColor

            return

        if self.container.check_box.active:
            self.container.check_box.active = False
        else:
            self.container.check_box.active = True

    def on_long_touch(self, *args):
        if self.__long_touch_event:
            self.select_image()

        self.__open_image = False

        def _callback(dt):
            self.__open_image = True

        Clock.schedule_once(callback=_callback, timeout=2)

    def on_press(self, *args):
        if self.parent.selected_items:
            self.select_image()

            self.__long_touch_event = False

            def _callback(dt):
                self.__long_touch_event = True

            Clock.schedule_once(callback=_callback, timeout=0.7)

    def on_release(self, *args):
        if self.__open_image:
            def _open_img_screen():
                app = MDApp.get_running_app()
                screen = app.root.get_screen('open_img_screen')
                screen.back_screen = app.root.current
                app.root.transition = RiseInTransition()
                app.root.current = 'open_img_screen'
                screen.ids.carousel.index = self.image.index
            try:
                if not self.parent.selected_items and not self.container.check_box:
                    _open_img_screen()
            except AttributeError as e:
                _open_img_screen()


class MySelectionList(MDGridLayout):
    selected_items = ListProperty()
    back_button = ObjectProperty()

    def __init__(self, **kwargs):
        super(MySelectionList, self).__init__(**kwargs)

    def selected_all(self):
        for smart_tile in self.children:
            if smart_tile not in self.selected_items:
                smart_tile.select_image()

    def unselected_all(self):
        for smart_tile in copy(self.selected_items):
            smart_tile.container.check_box.active = False

        app = MDApp.get_running_app()
        screen = app.root.get_screen('collection_screen')

        for button in copy(screen.ids.left_button.children):
            if isinstance(button, MDActionTopAppBarButton):
                self.parent.back_button = button
                screen.ids.left_button.remove_widget(button)

        if self.back_button:
            screen.ids.left_button.add_widget(self.back_button)

        screen.ids.button_delete.disabled = True
        screen.ids.button_delete.theme_icon_color = 'Custom'
        screen.ids.button_delete.icon_color = screen.md_bg_color




