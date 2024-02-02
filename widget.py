from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import dp
from kivy.properties import NumericProperty

from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import RiseInTransition

from kivymd.app import MDApp


class MyImage(AsyncImage):
    img_id = NumericProperty()
    index = NumericProperty()

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
        # if not self.disabled and self.collide_point(*touch.pos):
        #     if isinstance(self.parent.parent, MySelectionList) and self.parent.parent.get_selected():
        #         pass
        #     else:
        #         return self.open_img_screen()
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

    def open_img_screen(self):
        app = MDApp.get_running_app()
        screen = app.root.get_screen('open_img_screen')
        screen.back_screen = app.root.current
        app.root.transition = RiseInTransition()
        app.root.current = 'open_img_screen'
        screen.ids.carousel.index = self.index
        screen.ids.app_bar.title = 'x'.join(str(self.texture_size).split(', '))

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
