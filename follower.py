from typing import Any
import tls_client
from websocket import WebSocket
from json import loads, dumps
from console import printf as print, inputf as input
from os import _exit
import concurrent.futures


def getSocketID(): # not required (: maybe produce higher quality accs)
    ws = WebSocket()
    ws.connect("wss://ws-us2.pusher.com/app/eb1d5f283081a78b932c?protocol=7&client=js&version=7.6.0&flash=false")
    result = loads(ws.recv())
    socketID = loads(result.get("data")).get("socket_id")
    print("(~) SocketID -> %s" % socketID)
    return socketID

amt = 0

def sendFollow(user, cookies):
    global amt
    session = tls_client.Session(client_identifier="chrome_112", random_tls_extension_order=True)
    xsrf = cookies.get("XSRF-TOKEN").replace("%3D", "=")

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "authorization": f"Bearer {xsrf}",
        "connection": "keep-alive",
        "content-length": "0",
        "host": "kick.com",
        "origin": "https://kick.com",
        "referer": f"https://kick.com/{user}",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "x-socket-id": getSocketID(),
        "x-xsrf-token": xsrf
    }
    response = session.post(f'https://kick.com/api/v2/channels/{user}/follow', headers=headers, cookies=cookies)
    if "errors" in response.text:
        print(f"(-) {response.json().get('errors')}")
    elif response.status_code == 200:
        amt+=1
        print(f"(+) Followed {user} | {amt}")
    else:
        print(response.text)
        print(response.status_code)
        
            
            
if __name__ == "__main__":
    with open("accounts.txt", "r+") as f:
        accounts = [i.strip().split(":")[2] for i in f.readlines()]

    accounts = [account for account in accounts if account != "None"]
    accounts.reverse()
    
    user = input("User > ")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for account in accounts:
            cookie_string = account
            cookies = {}
            
            for i in range(1, 4):
                total = cookie_string.split("<Cookie ")[i].split(" for")[0]
                key = total.split("=")[0]
                value = total.split(" for")[0].replace(key + "=", "")
                cookies[key] = value
            
            try:
                total4 = cookie_string.split("<Cookie ")[4].split(" for")[0]
                key4 = total4.split("=")[0]
                value4 = total4.split(" for")[0].replace(key4+"=", "")
                cookies[key4] = value4
            except IndexError:
                pass
            
            if "__cf_bm" in cookies:
                del cookies["__cf_bm"]

            # print(cookies.keys())
            executor.submit(sendFollow, user, cookies)