import requests
from valo import cls, val, spinner, rateLimitDelay, lockDelay

def recieveChats():
    if len(val.chats) == 0:
        val.log(f"(ERROR) no chats moment | {val.chats}")
        #exit()
        return True
    
    while True:
        try:
            cls(val.player["name"])
            val.log(val.chats)
            ulog = int(val.log("enter chat num to return history", inputmode=True, newline=False))
            if ulog not in range(len(val.chats)): continue
            break
        except KeyboardInterrupt:
            cls(val.player["name"])
            return
        except: pass

    messages = requests.get(f"{val.localEndpoint}/chat/v6/messages?cid={val.chats[ulog]['cid']}", headers=val.basicAuth, verify=False)
    msgprint = [f"({msg["type"]}) {msg["game_name"]}#{msg["game_tag"]}: {msg["body"]}" for msg in messages.json()["messages"]]
    val.log(f'chats:\n {'\n '.join(msgprint)}', newline=False)
    return False


def sendChats():
    if len(val.chats) == 0:
        val.log(f"(ERROR) no chats moment | {val.chats}")
        return True
    
    while True:
        try:
            cls(val.player["name"])
            val.log(val.chats)
            ulog = int(val.log("enter chat num to send msg", inputmode=True, newline=False))
            if ulog not in range(len(val.chats)): continue
            break
        except KeyboardInterrupt:
            cls(val.player["name"])
            return
        except: pass

    msg = val.log("enter msg", inputmode=True, newline=False)
    messages = requests.post(f"{val.localEndpoint}/chat/v6/messages", json={"cid" : val.chats[ulog]['cid'], "message" : msg, "type" : val.chats[ulog]["type"]}, headers=val.basicAuth, verify=False)
    msgprint = [f"({msg["type"]}) {msg["game_name"]}#{msg["game_tag"]}: {msg["body"]}" for msg in messages.json()["messages"]]
    val.log(f'{'\n'.join(msgprint)}', newline=False)
    return False