import requests, argparse
from termcolor import colored
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

import consts
from val.valo import *
from features.instalock import instalock
from features.chat import *

# might just use richconsole ngl

cls(val.player["name"])

# parser = argparse.ArgumentParser()
# parser.add_argument(name="mode", help="the mode to use")
# args = vars(parser.parse_args())

modes = ["il", "rc", "sc"]
args = {"mode" : "instalock"}

def menu(user=True):
    while True:
        try:
            args["mode"] = LOGGER.print(f"enter mode ({', '.join(modes)})", inputmode=True, user=user).lower()
            if args["mode"] not in modes:
                cls(val.player["name"])
                LOGGER.print(f"enter a valid mode ({', '.join(modes)})")
                continue
        except KeyboardInterrupt:
            #exit()
            return 0
        except: continue
        cls(val.player["name"])
        break

user = True
while True:
    try:
        bruh = menu(user)
        if bruh == 0: break
        user = True
        match args["mode"]:
            case "il":
                instalock()
            case "rc":
                user = recieveChats()
                #LOGGER.print(requests.get(f"{val.localEndpoint}/chat/v6/conversations/ares-coregame", headers=val.basicAuth, verify=False).json())
            case "sc":
                user = sendChats()

    except KeyboardInterrupt: break
    except: pass

print("\n\n")