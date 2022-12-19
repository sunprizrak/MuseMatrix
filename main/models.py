class Image:
    images = []

    def __init__(self, data_image):
        for el in list(data_image.items()):
            self.__dict__[el[0]] = el[1]
        self.images.append(self)

    @classmethod
    def get_image(cls, image_id):
        for image in cls.images:
            if image.id == image_id:
                return image

    @classmethod
    def delete_image(cls, image_id):
        for image in cls.images:
            if image.id == image_id:
                cls.images.remove(image)


