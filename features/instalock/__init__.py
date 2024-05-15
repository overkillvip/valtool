import requests, base64, time, json, threading
from valo import cls, val, spinner, rateLimitDelay, lockDelay

"""
requests.get(f"{val.glzEndpoint}/pregame/v1/matches/{matchid}", headers=val.xHeaders)
can get enemy team characters and if locked in pre
"""
def instalock():
    # loop to always ask for agent even after locked from prev game
    while True:
        fastQuit = False
        try:
            
            # agent input loop until valid agent found
            while True:
                try:
                    ulog = val.log("enter agent name", inputmode=True).lower()
                    agentids = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()["data"]
                    agentid = [agent["uuid"] for agent in agentids if agent["displayName"].lower() == ulog.lower()][0]
                    break
                except KeyboardInterrupt:
                        cls(val.player["name"])
                        return False
                except Exception as e:
                    cls(val.player["name"])
                    val.log(f"(ERROR) {e}")

            # presence and matchid loop
            i = 0
            presence = None
            while True:
                timer = time.time()
                try:
                    cls(val.player["name"])
                    val.log(f"Finding match {spinner(i)}")
                    if i > 7: i = 0
                    i += 1

                    if not presence:
                        resp = requests.get(f"{val.localEndpoint}/chat/v4/presences", headers=val.basicAuth, verify=False, timeout=3).json()
                        presence = [user for user in resp["presences"] if user["puuid"] == val.player["puuid"] and json.loads(base64.b64decode(user["private"]))["sessionLoopState"] == "PREGAME"][0]
                        if len(presence) == 0: raise BufferError
                    # not else so it gets on same loop
                    if presence:
                        cls(val.player["name"])
                        val.log(f"GAMESTATE CHANGED {json.loads(base64.b64decode(presence["private"]))["sessionLoopState"]}")
                        matchid = requests.get(f"{val.glzEndpoint}/pregame/v1/players/{val.player['puuid']}", headers=val.xHeaders, timeout=3).json()["MatchID"]
                        val.log("FOUND MATCH")
                        # if not thread:
                        #     thread = threading.Thread(target=logLocks, args=(matchid))
                        #     thread.start()
                        break

                except KeyboardInterrupt:
                    cls(val.player["name"])
                    fastQuit = True
                    break
                except:
                    time.sleep(rateLimitDelay)
                    cls(val.player["name"])
            if fastQuit: continue

            # lock
            time.sleep(lockDelay)
            requests.post(f"{val.glzEndpoint}/pregame/v1/matches/{matchid}/select/{agentid}", headers=val.xHeaders)
            time.sleep(0.5)
            requests.post(f"{val.glzEndpoint}/pregame/v1/matches/{matchid}/lock/{agentid}", headers=val.xHeaders)
            val.log(f"LOCKED SUCCESSFULLY | {ulog} ({agentid}) in {time.time() - timer}s")

            logLocks(matchid)
            break
        
        # quit to menu
        except KeyboardInterrupt: break
        except: pass
    return False


def logLocks(matchid):
    try:
        time.sleep(0.5)
        agentresp = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()["data"]
        agents = {agent["uuid"] : agent["displayName"] for agent in agentresp}

        resp = requests.get(f"{val.glzEndpoint}/pregame/v1/matches/{matchid}", headers=val.xHeaders).json()
        for team in resp["Teams"]:
            players = {player["Subject"]: {
                "name" : "",
                "team" : team["TeamID"],
                "agent" : agents[player["CharacterID"]] if player["CharacterSelectionState"] == "locked" else "",
                "locked" : player["CharacterSelectionState"] == "locked",
                "logged" : False} for player in team["Players"]}

        puuids = list(players.keys())
        nameResp = requests.put(f"{val.pdEndpoint}/name-service/v2/players", headers=val.xHeaders, json=puuids)
        for player in nameResp.json():
            players[player["Subject"]]["name"] = f"{player['GameName']}#{player['TagLine']}"

        while True:
            # loop to get new player stats
            resp = requests.get(f"{val.glzEndpoint}/pregame/v1/matches/{matchid}", headers=val.xHeaders).json()
            for team in resp["Teams"]:
                for player in team["Players"]:
                    players[player["Subject"]]["agent"] = agents[player["CharacterID"]] if player["CharacterSelectionState"] == "locked" else ""
                    players[player["Subject"]]["locked"] = player["CharacterSelectionState"] == "locked"

            # print all players that are locked not logged already and once logged add to list
            for player in players:
                if player["locked"] and not player["logged"]:
                    val.log(f"NEW LOCKED AGENT {player['agent']} BY {players['name']} ON {'YOUR' if player['team'] == players[val.player['puuid']]['team'] else 'ENEMY'} TEAM", newline=False)
                    player["logged"] = True
            time.sleep(rateLimitDelay)

            # all users logged
            if all(player["logged"] for player in players): return True
    except Exception as e:
        return False