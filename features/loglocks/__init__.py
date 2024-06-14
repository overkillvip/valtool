import requests, time
from termcolor import colored
from val.valo import val, rateLimitDelay, LOGGER
from consts import consts


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
                for key, player in playersList.items():
                    if player["locked"] and not player["logged"]:
                        # fucking python
                        if len(set(player for player in playersList if playersList[player]["logged"])) == 5: print("\n")
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