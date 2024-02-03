from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.event import EventDispatcher
from kivy.graphics import Color, Ellipse, Line, Rectangle, StencilPush, StencilUse, StencilPop, ClearBuffers, \
    PushMatrix, MatrixInstruction, PopMatrix
from kivy.graphics.shader import Shader
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.image import AsyncImage, Image
from kivy.uix.stencilview import StencilView
from PIL import Image as PilImage, ImageDraw
from kivymd.app import MDApp


class EditImage(AsyncImage):
    texture_loaded = ObjectProperty()

    def __init__(self, **kwargs):
        super(EditImage, self).__init__(**kwargs)
        print(dir(self.canvas))

    def on_parent(self, widget, parent):
        if parent is not None:
            def _callback(dt):
                self.__update_before_canvas()

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

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            if self.collide_point(*touch.pos):
                texture = self.texture
                if texture:
                    # Получаем координаты касания относительно изображения
                    x, y = self.to_local(*touch.pos)

                    # Преобразуем координаты в координаты текстуры
                    tex_x = int((x / self.width) * texture.width)
                    tex_y = int((y / self.height) * texture.height)

                    # Преобразование байтов в bytearray
                    pixels = bytearray(texture.pixels)

                    # Устанавливаем альфа-канал в 0 (прозрачность) для выбранной области
                    pixels[tex_y * texture.width * 4 + tex_x * 4 + 3] = 0

                    # Преобразование bytearray обратно в байты
                    texture.pixels = bytes(pixels)

                    # Обновляем текстуру
                    texture.blit_buffer(bytes(pixels), colorfmt='rgba', bufferfmt='ubyte')

                    # Сбросим буфер, чтобы изменения вступили в силу
                    texture.ask_update()
            # setattr(self, 'rad', dp(32))
            # with self.canvas:
            #     # Color(1, 1, 1, 1)
            #     # setattr(self, 'rad', dp(32))
            #     # Ellipse(pos=(touch.x - self.rad/2, touch.y - self.rad/2), size=(self.rad, self.rad))
            #     # touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.rad/2)
            #     #
            #     Color(0, 0, 0, 0)
            #     Ellipse(pos=(touch.x - self.rad/2, touch.y - self.rad/2), size=(self.rad, self.rad))
            #
            return True
        for child in self.children[:]:
            if child.dispatch('on_touch_down', touch):
                return True

    # def on_touch_move(self, touch):
    #     if self.collide_point(*touch.pos):
    #         if touch.ud.get('line'):
    #             touch.ud['line'].points += (touch.x, touch.y)
    #         return True
    #     for child in self.children[:]:
    #         if child.dispatch('on_touch_move', touch):
    #             return True

    def on_touch_up(self, touch):

        for child in self.children[:]:
            if child.dispatch('on_touch_up', touch):
                return True

    def collide_point(self, x, y):
        # if self.size != self.texture_size:
        #     width, height = self.norm_image_size
        #     left = self.x + (self.width - width) / 2
        #     right = self.right - (self.right - (left + width))
        #     return left <= x <= right and self.y <= y <= self.top
        # return super(EditImage, self).collide_point(x, y)

        # Преобразуем координаты из глобальной системы координат в систему координат виджета
        local_x, local_y = self.to_widget(x, y)

        # Получаем размеры текстуры
        texture_width = 330
        texture_height = 330

        # Получаем границы текстуры изображения
        texture_left = self.center_x - texture_width / 2
        texture_right = self.center_x + texture_width / 2
        texture_bottom = self.center_y - texture_height / 2
        texture_top = self.center_y + texture_height / 2

        # Проверяем, находится ли точка в пределах текстуры
        return texture_left <= local_x <= texture_right and texture_bottom <= local_y <= texture_top

    def get_mask_image(self):
        texture = self.texture.create(size=self.texture_size, colorfmt='rgba')
        image = PilImage.new('RGBA', self.texture_size, 'white')

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