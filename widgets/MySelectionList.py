from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ObjectProperty, ListProperty
from kivymd.uix.behaviors import TouchBehavior, RectangularRippleBehavior
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.imagelist import MDSmartTile, MDSmartTileImage, MDSmartTileOverlayContainer
from kivymd.uix.selectioncontrol import MDCheckbox


class MySmartTileImage(MDSmartTileImage):
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

    def add_check_box(self):
        def _on_active_checkbox(obj, value):
            image = self.parent.image
            image.size_hint = (None, None)
            image.size = [image.size[0] - 20, image.size[1] - 20] if self.check_box.active else self.parent.size
            image.pos_hint = {'center_x': .5, 'center_y': .5}

            if self.check_box.active:
                if self.parent not in self.parent.parent.selected_items:
                    self.parent.parent.selected_items.append(self.parent)
            else:
                if self.parent in self.parent.parent.selected_items:
                    self.parent.parent.selected_items.remove(self.parent)

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
        self.md_bg_color = 'gray'
        self.long_touch_event = True

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

            return

        if self.container.check_box.active:
            self.container.check_box.active = False

            if len(self.parent.selected_items) == 0:
                for widget in self.parent.children:
                    widget.container.delete_check_box()
        else:
            self.container.check_box.active = True

        print(self.parent.selected_items)

    def on_long_touch(self, *args):
        if self.long_touch_event:
            self.select_image()

    def on_press(self, *args):
        if self.parent.selected_items:
            self.select_image()

            self.long_touch_event = False

            def _callback(dt):
                self.long_touch_event = True

            Clock.schedule_once(callback=_callback, timeout=0.7)


class MySelectionList(MDGridLayout):
    selected_items = ListProperty()

    def __init__(self, **kwargs):
        super(MySelectionList, self).__init__(**kwargs)

    # def select_all(self):
    #     for smart_tile in self.children:
    #         image = smart_tile.get_image()
    #
    #         if not image.check_box:
    #             image.add_check_box()





