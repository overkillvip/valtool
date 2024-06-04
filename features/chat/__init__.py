import requests
from val.valo import cls, val, spinner, rateLimitDelay, lockDelay, LOGGER

def recieveChats():
    if len(val.chats) == 0:
        LOGGER.print(f"(ERROR) no chats moment | {val.chats}")
        return False
    
    while True:
        try:
            cls(val.player["name"])
            LOGGER.print(val.chats)
            ulog = int(LOGGER.print("enter chat num to return history", inputmode=True, newlines=0))
            if ulog not in range(len(val.chats)): continue
            break
        except KeyboardInterrupt:
            cls(val.player["name"])
            return False
        except: pass

    messages = requests.get(f"{val.localEndpoint}/chat/v6/messages?cid={val.chats[ulog]['cid']}", headers=val.basicAuth, verify=False)
    msgprint = [f"({msg["type"]}) {msg["game_name"]}#{msg["game_tag"]}: {msg["body"]}" for msg in messages.json()["messages"]]
    LOGGER.print(f'chats:\n {'\n '.join(msgprint)}', newlines=0)
    return True


def sendChats():
    if len(val.chats) == 0:
        LOGGER.print(f"(ERROR) no chats moment | {val.chats}")
        return False
    
    while True:
        try:
            cls(val.player["name"])
            LOGGER.print(val.chats)
            ulog = int(LOGGER.print("enter chat num to send msg", inputmode=True, newlines=0))
            if ulog not in range(len(val.chats)): continue
            break
        except KeyboardInterrupt:
            cls(val.player["name"])
            return False
        except: pass

    msg = LOGGER.print("enter msg", inputmode=True, newlines=0)
    messages = requests.post(f"{val.localEndpoint}/chat/v6/messages", json={"cid" : val.chats[ulog]['cid'], "message" : msg, "type" : val.chats[ulog]["type"]}, headers=val.basicAuth, verify=False)
    msgprint = [f"({msg["type"]}) {msg["game_name"]}#{msg["game_tag"]}: {msg["body"]}" for msg in messages.json()["messages"]]
    LOGGER.print(f'{'\n'.join(msgprint)}', newlines=0)
    return True