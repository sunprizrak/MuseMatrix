class User:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __del__(self):
        User.__instance = None

    def update(self, data_user):
        if data_user:
            for el in zip(data_user.keys(), data_user.values()):
                self.__dict__[el[0]] = el[1]

    def __repr__(self):
        return self.email







