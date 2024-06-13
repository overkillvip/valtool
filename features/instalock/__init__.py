import requests, base64, time, json, threading
from termcolor import colored
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
    rules = consts.rules
    fastQuit = False
    ruleMode = False
    # loop to always ask for agent even after locked from prev game
    while True:
        loopAgain = False
        try:
            
            # agent input loop until valid agent found
            while True:
                try:
                    ulog = LOGGER.print("enter agent name", inputmode=True).lower()
                    if "+" in ulog:
                        ruleMode = True
                        ulog.replace("+", "")
                    agentids = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()["data"]
                    agents = {agent["displayName"].lower() : agent["uuid"] for agent in agentids}
                    if ulog not in agents:
                        cls(val.player["name"])
                        continue
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
                    if bruh.status_code == 400 and bruh.json()["errorCode"] == "BAD_CLAIMS" or bruh.status_code == 404:
                        val.refreshToken()
                        bruh = requests.get(f"{val.glzEndpoint}/{'pregame' if pregame else 'core-game'}/v1/players/{val.player['puuid']}", headers=val.xHeaders, timeout=3)

                    matchid = bruh.json()["MatchID"]
                    LOGGER.print("FOUND MATCH\n")
                    if not pregame:
                        fastQuit = True
                        break

                    agentid = agents[ulog.lower()]
                    # .keys() .split("\\")[-1]

                    resp = requests.get(f"{val.glzEndpoint}/pregame/v1/matches/{matchid}", headers=val.xHeaders)
                    if ruleMode: 
                        try:
                            for agent, value in rules.items():
                                if consts.maps[resp.json()["MapID"].split("/")[-1].lower()] in value["maps"]: agentid = agents[agent.lower()]
                        except: pass
                    
                    """
                    if ulog in rules and resp.json()["MapID"].split("/")[-1].lower() in rules[ulog]["maps"]: agentid = agents[rules[ulog]]
                    elif "*" in rules and resp.json()["MapID"].split("/")[-1].lower() in rules["*"]["maps"]: agentid = agents[rules["*"]["backup"]]
                    elif rules["icebox"] and "port" in resp.json()["MapID"].split("/")[-1].lower(): fastQuit = True
                    """
                    
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
            LOGGER.print(f"LOCKED SUCCESSFULLY | {ulog} ({agentid}) in {time.time() - timer}s ({time.time() - timer - lockDelay - 0.5})")
            break
        
        # quit to menu
        except KeyboardInterrupt: pass
        except: pass
    logLocks(matchid)
    return True

def logLocks(matchid):
    playersList = {}
    while True:
        try:
            # could do {'pregame' if gameState == "PREGAME" else 'core-game'} but no
            gameState = val.checkPresence()
            if gameState == "PREGAME": pregame = True
            elif gameState == "INGAME": pregame = False
            elif gameState == "MENUS": break
            else:
                time.sleep(rateLimitDelay)
                continue
            
            # get agents
            time.sleep(0.5 if pregame else 2)
            agentresp = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()["data"]
            agents = {agent["uuid"] : agent["displayName"] for agent in agentresp}

            # "locked" : player["CharacterSelectionState"] == "locked" if pregame else True
            resp = requests.get(f"{val.glzEndpoint}/{'pregame' if pregame else 'core-game'}/v1/matches/{matchid}", headers=val.xHeaders).json()

            if not pregame: resp["Teams"] = [{"Players" : resp["Players"]}]
            for team in resp["Teams"]:
                for player in team["Players"]:
                    if player["Subject"] in playersList: continue
                    playersList[player["Subject"]] = {
                        "name" : "",
                        "team" : team["TeamID"] if pregame else player["TeamID"],
                        "agent" : agents[player["CharacterID"].lower()] if not pregame or player["CharacterSelectionState"] == "locked" else "",
                        "streamer" : player["PlayerIdentity"]["Incognito"],
                        "locked" : player["CharacterSelectionState"] == "locked" if pregame else True,
                        "logged" : False
                    }  

            playersList = val.getNames(playersList)

            # loop to get new player stats
            while True:
                resp = requests.get(f"{val.glzEndpoint}/{'pregame' if pregame else 'core-game'}/v1/matches/{matchid}", headers=val.xHeaders).json()
                if not pregame: resp["Teams"] = [{"Players" : resp["Players"]}]
                for team in resp["Teams"]:
                    for player in team["Players"]:
                        playersList[player["Subject"]]["agent"] = agents[player["CharacterID"].lower()] if not pregame or player["CharacterSelectionState"] == "locked" else ""
                        playersList[player["Subject"]]["locked"] = player["CharacterSelectionState"] == "locked" if pregame else True

                # print all players that are locked, not logged already and once logged add to list
                # this is bugged for no fuckjing reason cant enum normally or through enumerate
                i = 0
                for key, player in playersList.items():
                    i += 1
                    #if i == 5: print("\n")
                    if player["locked"] and not player["logged"]:
                        LOGGER.print(f"NEW LOCKED AGENT {player['agent']} BY {colored(player['name'], 'magenta' if player['streamer'] else 'dark_grey')} {colored('ON', 'dark_grey')} {colored('YOUR', 'blue') if player['team'] == playersList[val.player['puuid']]['team'] else colored('ENEMY', 'red')} {colored('TEAM', 'dark_grey')}", newlines=1)
                        player["logged"] = True
                time.sleep(rateLimitDelay)

                # all users logged
                if all(player["logged"] for player in playersList.values()):
                    break
            
            # continue looping if its pregame so we can also get enemy team once gamestate changes to ingame (in match)
            if not pregame: break

        # error handling soontm
        except Exception as e:
            #return False
            pass
    return True


"""
 playersList = {player["Subject"]: {
                "name" : "",
                "team" : team["TeamID"] if pregame else player["TeamID"],
                "agent" : agents[player["CharacterID"]] if not pregame or player["CharacterSelectionState"] == "locked" else "",
                "locked" : player["CharacterSelectionState"] == "locked" if pregame else True,
                "logged" : False} for player in team["Players"] if player["Subject"] not in playersList}

"""