import requests, time
from termcolor import colored
from val.valo import val, rateLimitDelay, LOGGER
from consts import consts


class InstaLock():
    def __init__(self, matchid):
        self.agents: dict = val.getAgents()
        self.pregame: bool = False
        self.matchid: str = matchid
        self.playerList: dict[dict] = {}
        self.stage = lambda: 'pregame' if self.pregame else 'core-game'
        self.logLocks()


    # fuck with the val api and tell me better logic
    def logLocks(self):
        while True:
            try:
                # could do {'pregame' if gameState == "PREGAME" else 'core-game'} but no
                gameState = val.checkPresence()
                if gameState == "PREGAME": self.pregame = True
                elif gameState == "INGAME": self.pregame = False
                elif gameState == "MENUS": break
                else:
                    time.sleep(rateLimitDelay)
                    continue
                
                # get agents
                time.sleep(0.5 if self.pregame else 2)
                agents = self.agents

                resp = requests.get(f"{val.glzEndpoint}/{self.stage()}/v1/matches/{self.matchid}", headers=val.xHeaders).json()
                # i swear val purposely change their api convention to fuck shit
                if not self.pregame: resp["Teams"] = [{"Players" : resp["Players"]}]
                for team in resp["Teams"]:
                    for player in team["Players"]:
                        if player["Subject"] in self.playerList: continue
                        self.playerList[player["Subject"]] = {
                            "name" : "",
                            "team" : team["TeamID"] if self.pregame else player["TeamID"],
                            "agent" : agents[player["CharacterID"].lower()] if not self.pregame or player["CharacterSelectionState"] == "locked" else "",
                            "level" : player["PlayerIdentity"]["AccountLevel"],
                            "incognito" : player["PlayerIdentity"]["Incognito"],
                            "locked" : player["CharacterSelectionState"] == "locked" if self.pregame else True,
                            "logged" : False
                        }  

                self.playerList = val.getNames(self.playerList)

                # sex
                self.playerLoop()
                
                # continue looping if its pregame so we can also get enemy team once gamestate changes to ingame (in match)
                if not self.pregame: break

            # error handling soontm
            except Exception as e:
                #return False
                pass
        return self.playerList


    def playerLoop(self):
        agents = self.agents
        # loop to get new player stats
        while True:
            resp = requests.get(f"{val.glzEndpoint}/{self.stage()}/v1/matches/{self.matchid}", headers=val.xHeaders).json()
            if not self.pregame: resp["Teams"] = [{"Players" : resp["Players"]}]
            for team in resp["Teams"]:
                for player in team["Players"]:
                    self.playerList[player["Subject"]]["agent"] = agents[player["CharacterID"].lower()] if not self.pregame or player["CharacterSelectionState"] == "locked" else ""
                    self.playerList[player["Subject"]]["locked"] = player["CharacterSelectionState"] == "locked" if self.pregame else True

            # print all players that are locked, not logged already and once logged add to list
            # this is bugged for no fuckjing reason cant enum normally or through enumerate
            for key, player in self.playerList.items():
                if player["locked"] and not player["logged"]:
                    # fucking python
                    if len(set(player for player in self.playerList if self.playerList[player]["logged"])) == 5: print("\n")
                    LOGGER.print(f"NEW LOCKED AGENT {player['agent']} BY {colored(player['name'], 'magenta' if player['incognito'] else 'dark_grey')} {colored(player['level'], "light_blue")} {colored('ON', 'dark_grey')} {colored('YOUR', 'blue') if player['team'] == self.playerList[val.player['puuid']]['team'] else colored('ENEMY', 'red')} {colored('TEAM', 'dark_grey')}", newlines=1)
                    player["logged"] = True
            time.sleep(rateLimitDelay)

            # all users logged
            if all(player["logged"] for player in self.playerList.values()):
                break