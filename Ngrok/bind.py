import requests
import json
import os
from time import sleep
import datetime
from dotenv import load_dotenv
load_dotenv()

timer = int(os.getenv('sleep'))

def getTunnels():
    result = None
    while result is None:
        try:
            tunnels = os.getenv('tunnels')
            print('%s Trying %s'%(datetime.datetime.now(), tunnels))
            t = requests.get(tunnels)
            result = t.json()
        except:
            print('Waiting')
            sleep(10)
            pass
    return result

def updateTunnels(result):
    print('%s Updating Tunnels'%datetime.datetime.now())
    spaceId = os.getenv('spaceid')
    token = os.getenv('token')

    linksEndpoint = f"https://api.contentful.com/spaces/{spaceId}/entries?content_type=privateLink"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(linksEndpoint, headers=headers)
    linksResult = r.json()
    for tunnel in result["tunnels"]:
        link = next ((i for i in linksResult["items"] if i["fields"]["id"]["en-US"] == tunnel["name"]), None)
        if link != None and link["fields"]["url"]["en-US"] != tunnel["public_url"]:
            patchEndpoint = f'https://api.contentful.com/spaces/{spaceId}/entries/{link["sys"]["id"]}'
            patch = f'[{{"op": "replace", "path": "/fields/url/en-US", "value": "{tunnel["public_url"]}"}}]'
            patchHeaders = {"Authorization": f"Bearer {token}", "Content-type": "application/json-patch+json", "X-Contentful-Version": f'{link["sys"]["version"]}'}
            p = requests.patch(patchEndpoint, headers=patchHeaders, data=patch)
            patchResult = p.json()
            putEndpoint = patchEndpoint + "/published"
            putHeaders = patchHeaders = {"Authorization": f"Bearer {token}", "X-Contentful-Version": f'{patchResult["sys"]["version"]}'}
            put = requests.put(putEndpoint, headers=putHeaders)

def sameTunnels(tunnels, newTunnels):
    for tunnel in tunnels["tunnels"]:
        newtunnel = next ((i for i in newTunnels["tunnels"] if i["name"] == tunnel["name"]), None)
        if newtunnel is None:
            return False
        elif newtunnel["public_url"] != tunnel["public_url"]:
            return False
    return True


result = getTunnels()
updateTunnels(result)
while True:
    sleep(timer)
    newresult = getTunnels()
    if not sameTunnels(result, newresult):
        print('Tunnels are different')
        result=newresult
        updateTunnels(result)