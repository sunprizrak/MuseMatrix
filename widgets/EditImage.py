import io
from kivy.clock import Clock, mainthread
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
from PIL import Image as PILImage, ImageDraw
from kivymd.app import MDApp

class EditImage(AsyncImage):
    def __init__(self, **kwargs):
        super(EditImage, self).__init__(**kwargs)

    def on_parent(self, widget, parent):
        if parent is not None:
            def _callback(dt):
                self.__update_before_canvas()
                self.bind(norm_image_size=lambda x, y: self.__update_before_canvas())

            Clock.schedule_once(callback=_callback, timeout=2)

    @mainthread
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
            if self.texture:

                bottom = (self.height - self.norm_image_size[1]) / 2 + self.y

                tex_x = round((touch.x - self.x) / self.norm_image_size[0] * self.texture_size[0])
                tex_y = round((touch.y - bottom) / self.norm_image_size[1] * self.texture_size[1])

                # Преобразование байтов в bytearray
                pixels = bytearray(self.texture.pixels)

                # Радиус стирания
                erase_radius = 10  # Измените на необходимое значение

                # Определяем границы области стирания
                min_x = max(0, tex_x - erase_radius)
                max_x = min(self.texture_size[0], tex_x + erase_radius + 1)
                min_y = max(0, tex_y - erase_radius)
                max_y = min(self.texture_size[1], tex_y + erase_radius + 1)

                # Итерируем по окрестности точки касания
                for i in range(min_x, max_x):
                    for j in range(min_y, max_y):
                        # Вычисляем расстояние до точки касания
                        distance = ((i - tex_x) ** 2 + (j - tex_y) ** 2) ** 0.5

                        # Если расстояние меньше радиуса стирания, устанавливаем альфа-канал в 0
                        if distance <= erase_radius:
                            # Получаем абсолютные координаты в текстуре
                            abs_x = i
                            abs_y = j

                            # Устанавливаем альфа-канал в 0
                            pixels[abs_y * self.texture_size[0] * 4 + abs_x * 4 + 3] = 0

                # Создаем объект Texture с обновленными пикселями
                new_texture = self.texture.create(size=self.texture_size, colorfmt='rgba', bufferfmt='ubyte')
                new_texture.blit_buffer(bytes(pixels), colorfmt='rgba', bufferfmt='ubyte')
                # new_texture.flip_vertical()
                self.texture = new_texture

                # Обновляем виджет
                with self.canvas:
                    self.canvas.clear()
                    pos_x = self.center_x - self.norm_image_size[0] / 2
                    pos_y = self.center_y - self.norm_image_size[1] / 2
                    Rectangle(texture=self.texture, pos=(pos_x, pos_y), size=self.norm_image_size)



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