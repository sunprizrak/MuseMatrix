from kivy.properties import ObjectProperty
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import RiseInTransition


class MyImage(AsyncImage):
    sm = ObjectProperty()

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.full_screen()

    def collide_point(self, x, y):
        width, height = self.norm_image_size
        left = self.x + (self.width - width) / 2
        right = self.right - (self.right - (left + width))
        top = height
        return left <= x <= right and self.y <= y <= top

    def full_screen(self):
        self.sm.ids.open_img_screen.ids.full_image.source = self.source
        self.sm.transition = RiseInTransition()
        self.sm.ids.open_img_screen.ids.full_image.back_screen = self.sm.current
        self.sm.current = 'open_img_screen'