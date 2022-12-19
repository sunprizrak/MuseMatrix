from kivy.properties import ObjectProperty, ColorProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import RiseInTransition
from kivymd.uix.list import MDList
from kivymd.uix.selection import MDSelectionList
from kivymd.uix.selection.selection import SelectionItem, SelectionIconCheck


class MyImage(ButtonBehavior, AsyncImage):
    sm = ObjectProperty()
    img_id = NumericProperty()

    def on_release(self, *args):
        if isinstance(self.parent.parent, MySelectionList) and self.parent.parent.get_selected():
            pass
        else:
            self.full_screen()

    def collide_point(self, x, y):
        if self.size != self.norm_image_size:
            width, height = self.norm_image_size
            left = self.x + (self.width - width) / 2
            right = self.right - (self.right - (left + width))
            top = height
            return left <= x <= right and self.y <= y <= top
        return super(MyImage, self).collide_point(x, y)

    def full_screen(self):
        self.sm.ids.open_img_screen.ids.full_image.source = self.source
        self.sm.transition = RiseInTransition()
        self.sm.ids.open_img_screen.ids.full_image.back_screen = self.sm.current
        self.sm.ids.open_img_screen.ids.full_image.back_tab = self.sm.ids.main_screen.ids.navigation.current
        if self.sm.ids.main_screen.ids.navigation.current == 'collection':
            self.sm.ids.open_img_screen.ids.app_bar.right_action_items.insert(0, ['trash-can', lambda x: self.sm.ids.open_img_screen.delete(img_id=self.img_id, widget=self.parent)])
        self.sm.current = 'open_img_screen'


class MySelectionList(MDSelectionList):
    toolbar = ObjectProperty()
    progress_round_color = ColorProperty('#ed1c1c')

    def add_widget(self, widget, index=0, canvas=None):

        selection_icon = SelectionIconCheck(
            icon=self.icon,
            size_hint=(.2, .2),
            pos_hint={'center_x': .15, 'center_y': .85},
            md_bg_color=self.icon_bg_color,
            icon_check_color=self.icon_check_color,
        )

        selection_item = SelectionItem(
            size_hint=(1, 1),
            height=widget.height,
            instance_item=widget,
            instance_icon=selection_icon,
            overlay_color=self.overlay_color,
            progress_round_size=self.progress_round_size,
            progress_round_color=self.progress_round_color,
            owner=self,
        )

        selection_item.add_widget(widget)
        selection_item.add_widget(selection_icon)

        return super(MDList, self).add_widget(selection_item, index, canvas)

    def set_selection_mode(self, instance_selection_list, mode):
        if mode:
            self.toolbar.left_action_items.append(["close", lambda x: self.unselected_all()])
            self.toolbar.right_action_items.insert(0, ['trash-can', lambda x: False])

        else:
            self.toolbar.left_action_items.remove(self.toolbar.left_action_items[-1])
            self.toolbar.right_action_items.remove(self.toolbar.right_action_items[0])
            self.toolbar.title = ""

    def selected(self, instance_selection_list, instance_selection_item):
        self.toolbar.title = str(len(instance_selection_list.get_selected_list_items()))

    def unselected(self, instance_selection_list, instance_selection_item):
        if instance_selection_list.get_selected_list_items():
            self.toolbar.title = str(len(instance_selection_list.get_selected_list_items()))