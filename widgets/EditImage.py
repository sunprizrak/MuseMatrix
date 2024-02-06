from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.image import Image


class EditImage(Image):
    def __init__(self, **kwargs):
        super(EditImage, self).__init__(**kwargs)
        self.initial_texture = None
        self.updated_texture = None
        self.erase_percent = 4

    def on_parent(self, widget, parent):
        if parent is not None:
            def _callback(dt):
                self.__update_before_canvas()
                self.bind(norm_image_size=lambda x, y: self.__update_before_canvas())

            Clock.schedule_once(callback=_callback, timeout=0.1)

    def __update_before_canvas(self):
        self.canvas.before.clear()

        square_size = 10

        width, height = self.norm_image_size

        rows = int(height / square_size)
        cols = int(width / square_size)

        offset_x = (width - cols * square_size) / 2
        offset_y = (height - rows * square_size) / 2

        with self.canvas.before:
            for row in range(rows):
                for col in range(cols):
                    x = self.center_x - width / 2 + offset_x + col * square_size
                    y = self.center_y - height / 2 + offset_y + row * square_size

                    # Определение цвета квадрата в шахматном порядке
                    if (row + col) % 2 == 0:
                        Color(1, 1, 1, 1)  # Белый квадрат
                    else:
                        Color(0.5, 0.5, 0.5, 1)  # Серый квадрат

                    Rectangle(pos=(x, y), size=(square_size, square_size))

    def eraser_texture(self, touch):
        bottom = (self.height - self.norm_image_size[1]) / 2 + self.y

        if self.norm_image_size[0] != self.width:
            left = self.x + (self.width - self.texture_size[0]) / 2

            if self.texture_size[0] == self.texture_size[1]:
                tex_x = round(touch.x - left)
                tex_y = round(touch.y - bottom)
            else:
                left = self.x + (self.width - self.norm_image_size[0]) / 2
                tex_x = round((touch.x - left) / self.norm_image_size[0] * self.texture_size[0])
                tex_y = round((touch.y - bottom) / self.norm_image_size[1] * self.texture_size[1])
        else:
            tex_x = round((touch.x - self.x) / self.norm_image_size[0] * self.texture_size[0])
            tex_y = round((touch.y - bottom) / self.norm_image_size[1] * self.texture_size[1])


        # Проверяем ориентацию изображения и корректируем координаты при необходимости
        if self.texture.flip_vertical:
            tex_y = self.texture_size[1] - tex_y

        pixels = bytearray(self.texture.pixels)

        erase_radius = round(self.erase_percent * self.texture_size[0] / 100)  # %percent of texture_size

        min_x = max(0, tex_x - erase_radius)
        max_x = min(self.texture_size[0], tex_x + erase_radius + 1)
        min_y = max(0, tex_y - erase_radius)
        max_y = min(self.texture_size[1], tex_y + erase_radius + 1)

        for i in range(min_x, max_x):
            for j in range(min_y, max_y):
                distance = ((i - tex_x) ** 2 + (j - tex_y) ** 2) ** 0.5

                if distance <= erase_radius:
                    abs_x = i
                    abs_y = j

                    # Расчет одномерного индекса для изменения альфа-канала
                    index = abs_y * self.texture_size[0] * 4 + abs_x * 4 + 3

                    # Установка альфа-канала в 0
                    pixels[index] = 0


        # Создаем объект Texture с обновленными пикселями
        self.updated_texture = Texture.create(
            size=self.texture_size,
            colorfmt='rgba',
            bufferfmt='ubyte',
            mipmap=True,
        )

        self.updated_texture.blit_buffer(bytes(pixels), size=self.texture_size, colorfmt='rgba', bufferfmt='ubyte')
        self.updated_texture.flip_vertical()
        self.texture = self.updated_texture

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.texture:
                if not self.initial_texture:
                    self.initial_texture = self.texture
                self.eraser_texture(touch=touch)
            return True
        for child in self.children[:]:
            if child.dispatch('on_touch_down', touch):
                return True

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.eraser_texture(touch=touch)
            return True
        for child in self.children[:]:
            if child.dispatch('on_touch_move', touch):
                return True

    def collide_point(self, x, y):
        if self.size != self.norm_image_size:
            width, height = self.norm_image_size
            left = self.x + (self.width - width) / 2
            right = self.right - (self.right - (left + width))
            top = self.top - (self.height - height) / 2
            bottom = (self.height - height) / 2 + self.y
            return left <= x <= right and bottom <= y <= top
        return super(EditImage, self).collide_point(x, y)

    def get_mask_image(self):
        mask_img = CoreImage(self.texture)
        return mask_img

    def clear_eraser(self):
        if self.initial_texture:
            self.texture = self.initial_texture
            self.updated_texture = None