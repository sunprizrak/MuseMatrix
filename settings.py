from kivy.utils import platform

host_name = 'https://musematrix.de/'

# google ads
ID_REWARD_INTERSTITIAL = 'ca-app-pub-6164030233328943/3320939237'

if platform == 'linux':
    host_name = 'http://127.0.0.1:8000/'

