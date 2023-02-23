from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import sp, dp
from kivy.properties import ObjectProperty, ColorProperty, NumericProperty, ListProperty
from kivymd.uix.segmentedcontrol import MDSegmentedControl, MDSegmentedControlItem
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import RiseInTransition
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.selection import MDSelectionList
from kivymd.uix.selection.selection import SelectionItem, SelectionIconCheck


class MyImage(AsyncImage):
    sm = ObjectProperty()
    img_id = NumericProperty()

    def on_touch_down(self, touch):
        if self.disabled and self.collide_point(*touch.pos):
            with self.canvas:
                Color(.5, .8, .2, 1)
                setattr(self, 'rad', dp(32))
                Ellipse(pos=(touch.x - self.rad/2, touch.y - self.rad/2), size=(self.rad, self.rad))
                touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.rad/2)
            return True
        for child in self.children[:]:
            if child.dispatch('on_touch_down', touch):
                return True

    def on_touch_move(self, touch):
        if self.disabled and self.collide_point(*touch.pos):
            if touch.ud.get('line'):
                touch.ud['line'].points += (touch.x, touch.y)
            return True
        for child in self.children[:]:
            if child.dispatch('on_touch_move', touch):
                return True

    def on_touch_up(self, touch):
        if not self.disabled and self.collide_point(*touch.pos):
            if isinstance(self.parent.parent, MySelectionList) and self.parent.parent.get_selected():
                pass
            else:
                return self.full_screen()
        for child in self.children[:]:
            if child.dispatch('on_touch_up', touch):
                return True

    def collide_point(self, x, y):
        if self.size != self.norm_image_size:
            width, height = self.norm_image_size
            left = self.x + (self.width - width) / 2
            right = self.right - (self.right - (left + width))
            return left <= x <= right and self.y <= y <= self.top
        return super(MyImage, self).collide_point(x, y)

    def full_screen(self):
        if self.sm:
            self.sm.ids.open_img_screen.ids.full_image.source = self.source
            self.sm.transition = RiseInTransition()
            self.sm.ids.open_img_screen.ids.full_image.back_screen = self.sm.current
            if self.sm.current == 'collection_screen':
                self.sm.ids.open_img_screen.ids.app_bar.right_action_items.insert(0, ['trash-can', lambda x: self.sm.ids.open_img_screen.delete(img_id=self.img_id, widget=self.parent)])
            self.sm.current = 'open_img_screen'

    def get_mask_image(self):
        change_texture = self.texture.create(size=self.norm_image_size, colorfmt='rgba')

        # Get the pixel data from the texture
        pixels = bytearray(change_texture.pixels)

        # Modify the pixel data to set every pixel to red
        for i in range(0, len(pixels), 4):
            pixels[i] = 255  # red channel
            pixels[i + 1] = 0  # green channel
            pixels[i + 2] = 0  # blue channel
            pixels[i + 3] = 255  # alpha channel

        # Write the modified pixel data back to the texture
        change_texture.blit_buffer(pixels, colorfmt='rgba')

        self.texture = change_texture

        transparent_texture = self.texture.create(colorfmt='rgba')
        transparent_texture.mag_filter = 'linear'
        transparent_texture.min_filter = 'linear_mipmap_linear'

        cords = []

        width, height = self.norm_image_size
        left = self.x + (self.width - width) / 2

        for elem in self.canvas.children:
            if isinstance(elem, Line):
                for point in elem.points:
                    if len(cords) < 1:
                        cords.append([point - left - self.rad/2])
                    else:
                        if len(cords[-1]) < 2:
                            cords[-1].append(point - self.y - self.rad/2)
                        else:
                            cords.append([point - left - self.rad/2])

        # Cut out the part of the texture
        for cord in cords:
            self.texture.blit_buffer(transparent_texture.pixels, size=(self.rad, self.rad), pos=cord, colorfmt='rgba', bufferfmt='ubyte')

        mask_img = CoreImage(self.texture)

        return mask_img

    def clear_selection(self):
        if self.disabled:
            for el in self.canvas.children:
                if isinstance(el, Ellipse) or isinstance(el, Line):
                    self.canvas.children.remove(el)


class MySegmentedControl(MDSegmentedControl):

    def update_segment_panel_width(
        self, widget: MDSegmentedControlItem
    ) -> None:
        widget.text_size = (None, None)
        widget.font_size = sp(12)
        widget.texture_update()
        self.ids.segment_panel.width = dp(300)


class MySelectionList(MDSelectionList):
    screen: ObjectProperty()
    toolbar = ObjectProperty()
    progress_round_color = ColorProperty('#ed1c1c')
    back_item = ListProperty(['arrow-left'])

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
            self.toolbar.left_action_items.remove(self.toolbar.left_action_items[0])
            self.toolbar.left_action_items.append(["close", lambda x: self.unselected_all()])
            self.toolbar.right_action_items.insert(0, ['trash-can', lambda x: self.screen.delete_images(widget_list=instance_selection_list.get_selected_list_items())])
        else:
            self.toolbar.left_action_items.remove(self.toolbar.left_action_items[0])
            self.toolbar.left_action_items.append(self.back_item)
            self.toolbar.right_action_items.remove(self.toolbar.right_action_items[0])
            self.toolbar.title = ""

    def selected(self, instance_selection_list, instance_selection_item):
        self.toolbar.title = str(len(instance_selection_list.get_selected_list_items()))

    def unselected(self, instance_selection_list, instance_selection_item):
        if instance_selection_list.get_selected_list_items():
            self.toolbar.title = str(len(instance_selection_list.get_selected_list_items()))


class Message(OneLineListItem):

    def __init__(self, **kwargs):
        super(Message, self).__init__(**kwargs)
        self.ids._lbl_primary.shorten = False
        self.ids._lbl_primary.size_hint_y = 1

