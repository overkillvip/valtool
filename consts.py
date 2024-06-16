import json, requests
from config import config
from debug import DEBUG

class Consts():
    def __init__(self):
        self.config = config
        self.DEBUG = DEBUG
        self.rules = config["rules"]
        self.maps = {mapObj["mapUrl"].lower() : mapObj["displayName"].lower() for mapObj in requests.get("https://valorant-api.com/v1/maps").json()["data"]}

consts = Consts()