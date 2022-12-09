from .models import User


class UserController:
    host_name = 'http://127.0.0.1:8000/'
    path_data_user = host_name + 'auth/users/me/'

    def __init__(self, session):
        self.user = User()
        self.session = session

    def get_data_user(self):
        response = self.session.get(url=self.path_data_user)
        if response.status_code == 200:
            self.user.update(data_user=response.json())