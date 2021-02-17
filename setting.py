import json
with open("setting.json") as f:
    setting = json.load(f)


def getProps(prop):
    global setting
    try:
        return setting[prop]
    except Exception as err:
        return None


driverPath = getProps("driverPath")
url = getProps("url")
