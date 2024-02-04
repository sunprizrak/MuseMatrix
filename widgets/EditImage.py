import io
from kivy.clock import Clock, mainthread
from kivy.core.image import Image as CoreImage
from kivy.event import EventDispatcher
from kivy.graphics import Color, Ellipse, Line, Rectangle, StencilPush, StencilUse, StencilPop, ClearBuffers, \
    PushMatrix, MatrixInstruction, PopMatrix
from kivy.graphics.shader import Shader
from kivy.graphics.texture import Texture
from kivy.graphics.transformation import Matrix
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.image import Image
from kivy.uix.stencilview import StencilView
from PIL import Image as PILImage, ImageDraw
from kivymd.app import MDApp
import numpy as np


class EditImage(Image):
    def __init__(self, **kwargs):
        super(EditImage, self).__init__(**kwargs)
        self.initial_texture = self.texture
        self.updated_texture = None

    def on_parent(self, widget, parent):
        if parent is not None:
            def _callback(dt):
                self.__update_before_canvas()
                self.bind(norm_image_size=lambda x, y: self.__update_before_canvas())

            Clock.schedule_once(callback=_callback, timeout=2)

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

        if self.texture_size == self.norm_image_size:
            left = self.x + (self.width - self.texture_size[0]) / 2
            tex_x = round(touch.x - left)
            tex_y = round(touch.y - bottom)
        else:
            tex_x = round((touch.x - self.x) / self.norm_image_size[0] * self.texture_size[0])
            tex_y = round((touch.y - bottom) / self.norm_image_size[1] * self.texture_size[1])

        # Создаем новый массив, который можно изменять
        pixels = np.array(np.frombuffer(self.texture.pixels, dtype=np.uint8))
        pixels = pixels.reshape((self.texture_size[1], self.texture_size[0], 4))

        erase_radius = 10

        min_x = max(0, tex_x - erase_radius)
        max_x = min(self.texture_size[0], tex_x + erase_radius + 1)
        min_y = max(0, tex_y - erase_radius)
        max_y = min(self.texture_size[1], tex_y + erase_radius + 1)

        for i in range(min_x, max_x):
            for j in range(min_y, max_y):
                distance = np.linalg.norm(np.array([i - tex_x, j - tex_y]))

                if distance <= erase_radius:
                    pixels[j, i, 3] = 0

        # Создаем объект Texture с обновленными пикселями
        self.updated_texture = Texture.create(
            size=self.texture_size,
            colorfmt='rgba',
            bufferfmt='ubyte',
            mipmap=True,
        )

        self.updated_texture.blit_buffer(bytes(pixels), colorfmt='rgba', bufferfmt='ubyte')
        self.texture = self.updated_texture



    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.texture:
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
        texture = self.texture.create(size=self.texture_size, colorfmt='rgba')
        image = PILImage.new('RGBA', self.texture_size, 'white')

        # Создаем объект ImageDraw для рисования на изображении
        draw = ImageDraw.Draw(image)
        width, height = self.texture_size
        # Определяем размеры и положение прозрачной области (например, квадрата) в центре
        transparent_size = 50
        left = (width - transparent_size) // 2
        top = (height - transparent_size) // 2
        right = left + transparent_size
        bottom = top + transparent_size

        # Заполняем прозрачную область в альфа-канале нулевыми значениями
        draw.rectangle([left, top, right, bottom], fill=(0, 0, 0, 0))
        image.save('test_edit_image/test.png')
        # Get the pixel data from the texture
        # pixels = bytearray(change_texture.pixels)
        #
        # # Modify the pixel data to set every pixel to red
        # for i in range(0, len(pixels), 4):
        #     pixels[i] = 255  # red channel
        #     pixels[i + 1] = 0  # green channel
        #     pixels[i + 2] = 0  # blue channel
        #     pixels[i + 3] = 255  # alpha channel
        #
        # # Write the modified pixel data back to the texture
        # change_texture.blit_buffer(pixels, colorfmt='rgba')
        #
        # self.texture = change_texture
        #
        # transparent_texture = self.texture.create(colorfmt='rgba')
        # transparent_texture.mag_filter = 'linear'
        # transparent_texture.min_filter = 'linear_mipmap_linear'
        #
        # cords = []
        #
        # width, height = self.norm_image_size
        # left = self.x + (self.width - width) / 2
        #
        # for elem in self.canvas.children:
        #     if isinstance(elem, Line):
        #         for point in elem.points:
        #             if len(cords) < 1:
        #                 cords.append([point - left - self.rad/2])
        #             else:
        #                 if len(cords[-1]) < 2:
        #                     cords[-1].append(point - self.y - self.rad/2)
        #                 else:
        #                     cords.append([point - left - self.rad/2])
        #
        # # Cut out the part of the texture
        # for cord in cords:
        #     self.texture.blit_buffer(transparent_texture.pixels, size=(self.rad, self.rad), pos=cord, colorfmt='rgba', bufferfmt='ubyte')
        #
        # mask_img = CoreImage(self.texture)
        #
        # return mask_img

    def clear_selection(self):
        for el in self.canvas.children:
            if isinstance(el, Ellipse) or isinstance(el, Line):
                self.canvas.children.remove(el)