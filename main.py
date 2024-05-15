import requests, argparse, base64, os, re, time, json
from termcolor import colored
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from valo import *
from features.instalock import instalock
from features.chat import *

cls(val.player["name"])

# parser = argparse.ArgumentParser()
# parser.add_argument(name="mode", help="the mode to use")
# args = vars(parser.parse_args())

modes = ["il", "rc", "sc"]
args = {"mode" : "instalock"}

def menu(user=True):
    while True:
        try:
            args["mode"] = val.log(f"enter mode ({', '.join(modes)})", inputmode=True, user=user, newline=user).lower()
            if args["mode"] not in modes:
                cls(val.player["name"])
                val.log(f"enter a valid mode ({', '.join(modes)})")
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
                #val.log(requests.get(f"{val.localEndpoint}/chat/v6/conversations/ares-coregame", headers=val.basicAuth, verify=False).json())
            case "sc":
                user = sendChats()

    except KeyboardInterrupt: break
    except: pass

print("\n\n")