#!/usr/bin/env /usr/bin/python3

import os
import requests
import json

# ------------------------------------------------------------
def delete_file(fpath):
    if os.path.exists(fpath):
        os.remove(fpath)
# ------------------------------------------------------------
FILE_NAME_LIBRARY = 'spo_library.txt'
FILE_NAME_LIBRARY_RAW = 'spo_library_raw.txt'

ACCESS_TOKEN = os.getenv("access_token")
if ACCESS_TOKEN == None or ACCESS_TOKEN == "":
    print("Must set access_token env variable")
    exit(1)

delete_file(FILE_NAME_LIBRARY)
delete_file(FILE_NAME_LIBRARY_RAW)


library_file = open(FILE_NAME_LIBRARY, 'a')
library_file_raw = open(FILE_NAME_LIBRARY_RAW, 'a')
offset = 0
while True:
    rsp = requests.get(f'https://api.spotify.com/v1/me/tracks?limit=50&offset={offset}', headers={
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    })
    if rsp.status_code != 200:
        print(f"Invalid status code from spotify: {rsp.status_code}\n{rsp.text}")
        exit(2)
    else:
        offset += 50
    
    #print(rsp.text)

    json = json.loads(rsp.text)
    
    for item in json['items']:
        item = item['track']
        id = item['id']
        title = item['name']

        
        print(f'#{id} {title}')
        library_file.write(f'{id}\t{title}\n')
        library_file_raw.write(rsp.text)
    break

library_file.close()
library_file_raw.close()