import requests, base64, os, re, time, json
from termcolor import colored
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from utils import cls, spinner

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
            excep = False
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
                    break
                except Exception as e:
                    excep = True
                    i += 1
                    if i > 3: i = 0
                    cls(val.player["name"])
                    print(f"[CRITICAL] couldnt read lockfile/localendpoint | {e}")
                    print(f"Waiting for game{'.' * i}")
                    time.sleep(1)

            if excep: time.sleep(10)

            try:
                with open(f"{os.getenv('localappdata')}\\VALORANT\\Saved\\Logs\\ShooterGame.log", "r") as logFile:
                    self.logFileData = logFile.read()
            except Exception as e:
                print(f"[CRITICAL] couldnt read logfile | {e}")
                exit()
            
            self.basicToken =  base64.b64encode(f'riot:{self.lockFile["password"]}'.encode()).decode("utf-8")
            self.basicAuth = {"Authorization" : f"Basic {self.basicToken}"}

            self.client = {
                "platform" : "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
                "version" : list(requests.get(f"{self.localEndpoint}/product-session/v1/external-sessions", headers=self.basicAuth, verify=False).json().values())[-1]["version"]
            }

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
            #self.geo = requests.put("https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant", json={"id_token" : ""}, headers=self.bearerAuth, verify=False).json()

            convoResp = requests.get(f"{self.localEndpoint}/chat/v6/conversations", headers=self.basicAuth, verify=False).json()
            self.chats = {i : chat for i, chat in enumerate(convoResp["conversations"])} if len(convoResp) > 0 else {}

        except Exception as e:
            print(f"[CRITICAL] unkown excep | {e}")
            exit()
    
    def log(self, msg, inputmode=False, user=True, newline=True):
        #if user: print(f"\n{prefix} {colored(val.player['name'], "light_magenta", attrs=["blink", "bold"])}")
        print(f"\n{'\n' if newline else ''}{prefix} " + colored(msg, color) + ("\n" if not inputmode and not newline else ""))
        if inputmode: return input(colored("   > ", color))

val = valor()