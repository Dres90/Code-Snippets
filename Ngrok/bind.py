import requests
import json
import os
from time import sleep
from dotenv import load_dotenv
load_dotenv()



t = requests.get(os.getenv('tunnels'))
result = t.json()

spaceId = os.getenv('spaceid')
token = os.getenv('token')

linksEndpoint = f"https://api.contentful.com/spaces/{spaceId}/entries?content_type=privateLink"
headers = {"Authorization": f"Bearer {token}"}
linkResult = None
while linkResult is None:
    try:
        r = requests.get(linksEndpoint, headers=headers)
        linksResult = r.json()
    except:
        sleep(10)
        pass
for tunnel in result["tunnels"]:
    link = next ((i for i in linksResult["items"] if i["fields"]["id"]["en-US"] == tunnel["name"]), None)
    if link != None:
        patchEndpoint = f'https://api.contentful.com/spaces/{spaceId}/entries/{link["sys"]["id"]}'
        patch = f'[{{"op": "replace", "path": "/fields/url/en-US", "value": "{tunnel["public_url"]}"}}]'
        patchHeaders = {"Authorization": f"Bearer {token}", "Content-type": "application/json-patch+json", "X-Contentful-Version": f'{link["sys"]["version"]}'}
        p = requests.patch(patchEndpoint, headers=patchHeaders, data=patch)
        patchResult = p.json()
        putEndpoint = patchEndpoint + "/published"
        putHeaders = patchHeaders = {"Authorization": f"Bearer {token}", "X-Contentful-Version": f'{patchResult["sys"]["version"]}'}
        put = requests.put(putEndpoint, headers=putHeaders)