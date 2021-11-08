
import json
path = './store.json'


def resolveJson(path):
    file = open(path, "rb")
    fileJson = json.load(file)[0]
    name = fileJson["name"]
    code = fileJson["code"]
    portion = fileJson["portion"]
    start_cach = fileJson["start_cach"]
    return {'name': name, 'code': code, 'portion': portion, 'start_cach': start_cach}

def output():
    print(resolveJson(path)['name'])


output()
