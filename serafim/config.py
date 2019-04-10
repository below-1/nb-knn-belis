from environs import Env

env = Env()
env.read_env()

APP_SECRET = env.str("APP_SECRET")
DATABASE_URI = env.str("DATABASE_URI")

class DsetCodeRule:
    def __init__(self):
        self.rules = None

    def save(self, rules):
        pass

    def _reload(self):
        pass