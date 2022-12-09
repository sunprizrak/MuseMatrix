class User:

    def update(self, data_user):
        if data_user:
            for el in zip(data_user.keys(), data_user.values()):
                self.__dict__[el[0]] = el[1]

    def __repr__(self):
        return self.email








