import json
from config import config
from debug import DEBUG

class Consts():
    def __init__(self):
        self.config = config
        self.DEBUG = DEBUG
        self.rules = config["rules"]

consts = Consts()