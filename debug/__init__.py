from config import config

"""
TODO
 - load dictionary as class __dict__ = class -> dict (used in raccoon for server data, saving to file)
"""

class Debug():
    def __init__(self):
        self.data = config["debug"]
        self.level = self.data["level"]
        self.verbose = self.data["verbose"]

DEBUG = Debug()