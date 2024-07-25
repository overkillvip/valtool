import requests
from val.valo import cls, val, spinner, rateLimitDelay, lockDelay, LOGGER


class Chats():
    def __init__(self):
        convoResp = requests.get(f"{val.localEndpoint}/chat/v6/conversations", headers=val.basicAuth, verify=False).json()
        self.chats = {i : chat for i, chat in enumerate(convoResp["conversations"])} if len(convoResp) > 0 else {}


    def recieveChats(self):
        if len(self.chats) == 0:
            LOGGER.print(f"(ERROR) no chats moment | {self.chats}")
            return False
        
        while True:
            try:
                cls(val.player["name"])
                LOGGER.print(self.chats)
                ulog = int(LOGGER.print("enter chat num to return history", inputmode=True, newlines=2))
                if ulog not in range(len(self.chats)): continue
                break
            except KeyboardInterrupt:
                cls(val.player["name"])
                return False
            except: pass

        messages = requests.get(f"{val.localEndpoint}/chat/v6/messages?cid={self.chats[ulog]['cid']}", headers=val.basicAuth, verify=False)
        msgprint = [f"({msg["type"]}) {msg["game_name"]}#{msg["game_tag"]}: {msg["body"]}" for msg in messages.json()["messages"]]
        LOGGER.print(f'chats:\n {'\n '.join(msgprint)}', newlines=0)
        return True


    def sendChats(self):
        if len(self.chats) == 0:
            LOGGER.print(f"(ERROR) no chats moment | {self.chats}")
            return False
        
        while True:
            try:
                cls(val.player["name"])
                LOGGER.print(self.chats)
                ulog = int(LOGGER.print("enter chat num to send msg", inputmode=True, newlines=2))
                if ulog not in range(len(self.chats)): continue
                break
            except KeyboardInterrupt:
                cls(val.player["name"])
                return False
            except: pass

        msg = LOGGER.print("enter msg", inputmode=True, newlines=0)
        messages = requests.post(f"{val.localEndpoint}/chat/v6/messages", json={"cid" : self.chats[ulog]['cid'], "message" : msg, "type" : self.chats[ulog]["type"]}, headers=val.basicAuth, verify=False)
        msgprint = [f"({msg["type"]}) {msg["game_name"]}#{msg["game_tag"]}: {msg["body"]}" for msg in messages.json()["messages"]]
        LOGGER.print(f'{'\n'.join(msgprint)}', newlines=0)
        return True