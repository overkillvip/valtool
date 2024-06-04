import requests, base64, time, json, threading
from val.valo import cls, val, spinner, rateLimitDelay, lockDelay, LOGGER
from consts import consts

"""
requests.get(f"{val.glzEndpoint}/pregame/v1/matches/{matchid}", headers=val.xHeaders)
can get enemy team characters and if locked in pre | nvm dont think it responds with enemy team in pre
yes again ik the fastquit and loopagain are aids idc this wasnt meant to be released
"""
def instalock():
    # blacklist = {
    #     "*" : {"backup" : "cypher", "maps" : ["sunset", "bind", "breeze"]},
    #     "cypher" : {"backup" : "neon", "maps" : ["icebox"]},
    #     "neon" : {"backup" : "cypher", "maps" : ["sunset", "bind", "breeze"]}
    #     }
    blacklist = consts.blacklist
    fastQuit = False
    # loop to always ask for agent even after locked from prev game
    while True:
        loopAgain = False
        try:
            
            # agent input loop until valid agent found
            while True:
                try:
                    ulog = LOGGER.print("enter agent name", inputmode=True).lower()
                    agentids = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()["data"]
                    agents = {agent["displayName"].lower() : agent["uuid"] for agent in agentids}
                    break
                except KeyboardInterrupt:
                        cls(val.player["name"])
                        return False
                except Exception as e:
                    cls(val.player["name"])
                    LOGGER.print(f"(ERROR) {e}")
                    return False

            """
            matchid loop
            do presence cuz it replicates game behaviour and we arent spamming a arbitrary endpoint every second
            ik the spinner is aids ill just use a ui lib next time
            """
            i = 0
            while True:
                timer = time.time()
                try:
                    cls(val.player["name"])
                    LOGGER.print(f"Finding match {spinner(i)}")
                    if i > 7: i = 0
                    i += 1

                    # presence check
                    gameState = val.checkPresence()
                    # no ternary cuz menus
                    if gameState == "PREGAME": pregame = True
                    elif gameState == "INGAME": pregame = False
                    else: raise TimeoutError


                    cls(val.player["name"])
                    LOGGER.print(f"GAMESTATE CHANGED {gameState}")
                    bruh = requests.get(f"{val.glzEndpoint}/{'pregame' if pregame else 'core-game'}/v1/players/{val.player['puuid']}", headers=val.xHeaders, timeout=3)
                    if bruh.status_code == 400 and bruh.json()["errorCode"] == "BAD_CLAIMS":
                        val.refreshToken()
                        bruh = requests.get(f"{val.glzEndpoint}/{'pregame' if pregame else 'core-game'}/v1/players/{val.player['puuid']}", headers=val.xHeaders, timeout=3)

                    matchid = bruh.json()["MatchID"]
                    LOGGER.print("FOUND MATCH")
                    if not pregame:
                        fastQuit = True
                        break
                    agentid = agents[ulog]
                    # .keys() .split("\\")[-1]
                    resp = requests.get(f"{val.glzEndpoint}/pregame/v1/matches/{matchid}", headers=val.xHeaders)
                    if ulog in blacklist and resp.json()["MapID"].split("/")[-1].lower() in blacklist[ulog]["maps"]: agentid = agents[blacklist[ulog]["backup"]]
                    elif "*" in blacklist and resp.json()["MapID"].split("/")[-1].lower() in blacklist["*"]["maps"]: agentid = agents[blacklist["*"]["backup"]]
                    # if not thread:
                    #     thread = threading.Thread(target=logLocks, args=(matchid))
                    #     thread.start()
                    break

                except KeyboardInterrupt:
                    cls(val.player["name"])
                    loopAgain = True
                    break
                except Exception as e:
                    time.sleep(rateLimitDelay)
                    cls(val.player["name"])
            if loopAgain: continue
            if fastQuit: break

            # lock
            time.sleep(lockDelay)
            requests.post(f"{val.glzEndpoint}/pregame/v1/matches/{matchid}/select/{agentid}", headers=val.xHeaders)
            time.sleep(0.5)
            requests.post(f"{val.glzEndpoint}/pregame/v1/matches/{matchid}/lock/{agentid}", headers=val.xHeaders)
            LOGGER.print(f"LOCKED SUCCESSFULLY | {ulog} ({agentid}) in {time.time() - timer}s ({time.time() - timer - lockDelay})")
            break
        
        # quit to menu
        except KeyboardInterrupt: pass
        except: pass
    logLocks(matchid)
    return True

def logLocks(matchid):
    players = {}
    while True:
        try:
            # could do {'pregame' if gameState == "PREGAME" else 'core-game'} but no
            gameState = val.checkPresence()
            if gameState == "PREGAME": pregame = True
            elif gameState == "INGAME": pregame = False
            else:
                time.sleep(rateLimitDelay)
                continue
            
            time.sleep(0.5 if pregame else 2)
            agentresp = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()["data"]
            agents = {agent["uuid"] : agent["displayName"] for agent in agentresp}

            resp = requests.get(f"{val.glzEndpoint}/{'pregame' if pregame else 'core-game'}/v1/matches/{matchid}", headers=val.xHeaders).json()
            if not pregame: resp["Teams"] = [{"Players" : resp["Players"]}]
            for team in resp["Teams"]:
                players = {player["Subject"]: {
                "name" : "",
                "team" : team["TeamID"] if pregame else player["TeamID"],
                "agent" : agents[player["CharacterID"]] if player["CharacterSelectionState"] == "locked" else "",
                "locked" : player["CharacterSelectionState"] == "locked",
                "logged" : False} for player in team["Players"] if player["Subject"] not in players}

            puuids = list(players.keys())
            nameResp = requests.put(f"{val.pdEndpoint}/name-service/v2/players", headers=val.xHeaders, json=puuids)
            for player in nameResp.json():
                players[player["Subject"]]["name"] = f"{player['GameName']}#{player['TagLine']}"

            # loop to get new player stats
            while True:
                resp = requests.get(f"{val.glzEndpoint}/{'pregame' if pregame else 'core-game'}/v1/matches/{matchid}", headers=val.xHeaders).json()
                for team in resp["Teams"]:
                    for player in team["Players"]:
                        players[player["Subject"]]["agent"] = agents[player["CharacterID"]] if player["CharacterSelectionState"] == "locked" else ""
                        players[player["Subject"]]["locked"] = player["CharacterSelectionState"] == "locked"

                # print all players that are locked, not logged already and once logged add to list
                # this is bugged for no fuckjing reason cant enum normally or through enumerate
                for key, player in enumerate(players):
                    player = players[player]
                    if player["locked"] and not player["logged"]:
                        LOGGER.print(f"NEW LOCKED AGENT {player['agent']} BY {player['name']} ON {'YOUR' if player['team'] == players[val.player['puuid']]['team'] else 'ENEMY'} TEAM", newlines=0)
                        player["logged"] = True
                time.sleep(rateLimitDelay)

                # all users logged
                if all(player["logged"] for player in players.items()): break
            if not pregame: break
        # error handling soontm
        except Exception as e:
            #return False
            pass
    return True
