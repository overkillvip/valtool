import requests, base64, os, re, time, json
from termcolor import colored
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from inspect import stack

# scuffed ill change tmrw its 1am and i have to drive tmrw
from utils import cls, spinner, LOGGER

rsPattern = r"https://glz-(.+?)-1.(.+?).a.pvp.net"
lockDelay = 4
rateLimitDelay = 2

color = "dark_grey"
prefix = f"{colored('[', color)}{colored('$', 'magenta')}{colored(']', color)}"
class valor():
    def __init__(self):
        try:
            # name:pid:port:password:protocol
            i = 0
            excep = "lock"
            while True:
                try:
                    with open(f"{os.getenv('localappdata')}\\Riot Games\\Riot Client\\Config\\lockfile", "r") as lockFile:
                        self.lockFileData = lockFile.read()
                    data = self.lockFileData.split(":")
                    self.lockFile = {
                        "name" : data[0],
                        "pid" : data[1],
                        "port" : data[2],
                        "password" : data[3],
                        "protocol" : data[4]
                    }
                    self.localEndpoint = f'https://127.0.0.1:{self.lockFile["port"]}'
                    if requests.get(f"{self.localEndpoint}/product-session/v1/external-sessions", verify=False).status_code != 401: raise BufferError

                    with open(f"{os.getenv('localappdata')}\\VALORANT\\Saved\\Logs\\ShooterGame.log", "r") as logFile:
                        excep = "log"
                        self.logFileData = logFile.read()
                        re.search(rsPattern, self.logFileData).group(0)
                    excep = False
                    break
                except Exception as e:
                    i += 1
                    if i > 3: i = 1
                    cls()
                    LOGGER.log(stack()[0][3], f"Couldnt read {'lockfile/localendpoint' if excep != 'log' else 'logfile'} | {e}", "error")
                    print(f"Waiting for game{'.' * i}")
                    time.sleep(1)

            # game init thai ming moment
            if excep: time.sleep(10)
            
            self.basicToken =  base64.b64encode(f'riot:{self.lockFile["password"]}'.encode()).decode("utf-8")
            self.basicAuth = {"Authorization" : f"Basic {self.basicToken}"}
            # y no bearer
            # doesnt matter about printing its local
            LOGGER.log(stack()[0][3], f"Retrieved basic auth header value {self.basicToken}", "debug")

            self.client = {
                "platform" : "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
                "version" : list(requests.get(f"{self.localEndpoint}/product-session/v1/external-sessions", headers=self.basicAuth, verify=False).json().values())[-1]["version"]
            }

            LOGGER.log(stack()[0][3], f"Retrieved version {self.client['version']}", "debug")

            # X-Headers (remote endpoints)
            self.refreshToken()

            regexThing = re.search(rsPattern, self.logFileData)
            self.region = regexThing.group(1)
            self.shard = regexThing.group(2)
            self.glzEndpoint = f"https://glz-{self.region}-1.{self.shard}.a.pvp.net"
            self.pdEndpoint = f"https://pd.{self.shard}.a.pvp.net"

            self.chatResp = requests.get(f"{self.localEndpoint}/chat/v1/session", headers=self.basicAuth, verify=False).json()
            self.player = {
                "name" : f'{self.chatResp["game_name"]}#{self.chatResp["game_tag"]}',
                "puuid" : self.chatResp["puuid"]
            }
            LOGGER.log(stack()[0][3], f"Loaded player {self.player}", "debug")
            #self.geo = requests.put("https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant", json={"id_token" : ""}, headers=self.bearerAuth, verify=False).json()

            """
            convoResp = requests.get(f"{self.localEndpoint}/chat/v6/conversations", headers=self.basicAuth, verify=False).json()
            self.chats = {i : chat for i, chat in enumerate(convoResp["conversations"])} if len(convoResp) > 0 else {}
            """
            #self.agents = self.getAgents()

        except Exception as e:
            LOGGER.log(stack()[0][3], f"Unhandled excep | {e}", "critical")
        
    def refreshToken(self):
        LOGGER.log(stack()[0][3], "Refreshing remote endpoint auth headers", "debug")
        self.entitlements = requests.get(f"{self.localEndpoint}/entitlements/v1/token", headers=self.basicAuth, verify=False).json()
        self.entitlementToken = self.entitlements["token"]
        self.bearerToken = self.entitlements["accessToken"]
        self.bearerAuth = {"Authorization" : f"Bearer {self.bearerToken}"}
        self.xHeaders = {
            "X-Riot-ClientPlatform": self.client["platform"],
            "X-Riot-ClientVersion": self.client["version"],
            "X-Riot-Entitlements-JWT": self.entitlementToken,
            "Authorization": f"Bearer {self.bearerToken}"
        }
        LOGGER.log(stack()[0][3], "Succesfully refreshed remote endpoint auth headers", "debug")
    
    def checkPresence(self):
        resp = requests.get(f"{val.localEndpoint}/chat/v4/presences", headers=self.basicAuth, verify=False, timeout=3).json()
        # presence = [user for user in resp["presences"] if user["puuid"] == val.player["puuid"] and json.loads(base64.b64decode(user["private"]))["sessionLoopState"] == "PREGAME"][0]
        # if len(presence) == 0: raise BufferError
        presence = [user for user in resp["presences"] if user["puuid"] == val.player["puuid"]]
        if len(presence) == 0: return False
        gameState = json.loads(base64.b64decode(presence[0]["private"]))["sessionLoopState"]

        LOGGER.log(stack()[0][3], f"Presence changed {gameState}", type="debug", level=2)
        return gameState
    
    def getNames(self, playersList: dict):
        # get names
        puuids = list(playersList.keys())
        nameResp = requests.put(f"{val.pdEndpoint}/name-service/v2/players", headers=val.xHeaders, json=puuids)
        for player in nameResp.json():
            playersList[player["Subject"]]["name"] = f"{player['GameName']}#{player['TagLine']}"

        return playersList
    
    def getAgents(self, byId=True):
        agentids = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()["data"]
        if byId: agents = {agent["uuid"] : agent["displayName"].lower() for agent in agentids}
        else: agents = {agent["displayName"].lower() : agent["uuid"] for agent in agentids}
        return agents

val = valor()