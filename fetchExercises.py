import requests as requests

def fetchAllExercises():
    resp = requests.get("https://wger.de/api/v2/exercise/?limit=500&offset=0")
    json_resp = resp.json()
    for result in json_resp['results']:
        print({result['name']:result['id']})


fetchAllExercises()