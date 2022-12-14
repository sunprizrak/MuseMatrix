class Image:
    images = []

    def __init__(self, data_image):
        for el in list(data_image.items()):
            self.__dict__[el[0]] = el[1]
        self.images.append(self)

    def update(self, data_image):
        for el in list(data_image.items()):
            self.__dict__[el[0]] = el[1]