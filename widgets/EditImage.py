from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from PIL import Image as PILImage, ImageDraw
import asynckivy as ak


class EditImage(Image):
    def __init__(self, **kwargs):
        super(EditImage, self).__init__(**kwargs)
        self.initial_texture = None
        self.erase_percent = 5

        texture = self.__create_new_texture()
        self.texture = texture

        # Create pill image mask with white pixels
        self.pill_mask = PILImage.new('L', self.texture_size, 255)

        # Create pill image for pill image mask
        self.pil_image = PILImage.open(self.source).convert('RGBA')

    def on_parent(self, widget, parent):
            if parent is not None:
                def _callback(dt):
                    self.__update_before_canvas()
                    self.bind(norm_image_size=lambda x, y: self.__update_before_canvas())

                Clock.schedule_once(callback=_callback, timeout=0.1)

    def __create_new_texture(self):
        texture = Texture.create(
            size=self.texture_size,
            colorfmt='rgba',
            bufferfmt='ubyte',
            mipmap=True,
        )

        texture.blit_buffer(bytes(self.texture.pixels), size=self.texture_size, colorfmt='rgba', bufferfmt='ubyte')
        texture.flip_vertical()
        return texture

    def __update_before_canvas(self):
        self.canvas.before.clear()

        square_size = 20

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

    async def __apply_mask(self, mask):
        self.pil_image.putalpha(mask)  # Применяем маску к изображению через альфа-канал
        self.texture.blit_buffer(self.pil_image.tobytes(), size=self.texture_size, colorfmt='rgba', bufferfmt='ubyte')
        self.canvas.ask_update()

    async def __create_transparent_circle(self, touch):
        erase_radius = round(self.erase_percent * self.texture_size[0] / 100)
        tex_x, tex_y = await self.__calculate_texture_coordinates(touch=touch)

        draw = ImageDraw.Draw(self.pill_mask)
        draw.ellipse((tex_x - erase_radius, tex_y - erase_radius, tex_x + erase_radius, tex_y + erase_radius), fill=0)  # Рисуем круг на маске

        await self.__apply_mask(self.pill_mask)

    async def __calculate_texture_coordinates(self, touch):
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

        if self.texture.flip_vertical:
            tex_y = self.texture_size[1] - tex_y

        return tex_x, tex_y

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.texture:
                if not self.initial_texture:
                    texture = self.__create_new_texture()
                    self.initial_texture = texture
                ak.start(self.__create_transparent_circle(touch=touch))
            return True
        for child in self.children[:]:
            if child.dispatch('on_touch_down', touch):
                return True

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            ak.start(self.__create_transparent_circle(touch=touch))
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
            self.initial_texture = None
            self.pill_mask = PILImage.new('L', self.texture_size, 255)