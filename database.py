import json
from logger import logger
from cowin import getStates, getDistricts
from threading import Lock
import re
import copy


##### To get the state information dump #####
# states = getStates()
# states = getDistricts(states)
# with open('data', 'w') as f:
#     json.dump(states, f, indent=4)
#############################################

####### To load the state information #######
with open('data', 'r') as f:
    states = json.load(f)
#############################################


users = {}
search_data = {
    "pincode": {},
    "district": {}
}

lock = Lock()


def getStateName(pattern: str):
    match = []
    for key in states.keys():
        if re.search(pattern, key, re.IGNORECASE):
            match.append(key)
    if len(match) < 1 or len(match) > 3:
        return None
    elif len(match) == 1 and pattern.lower() == match[0].lower():
        return match[0]
    else:
        return match


def getDistrictName(pattern: str, state: str):
    districts = states[state]["districts"]
    match = []
    for key in districts.keys():
        if re.search(pattern, key, re.IGNORECASE):
            match.append(key)
    if len(match) < 1 or len(match) > 3:
        return None
    elif len(match) == 1 and pattern.lower() == match[0].lower():
        return match[0]
    else:
        return match


def getStateCode(name: str):
    return states[name]["state_id"]


def getDistrictCode(state_name: str, district_name: str):
    return states[state_name]["districts"][district_name]


def checkUser(id: str):
    with lock:
        if id in users:
            return True
        return False


def getUser(id: str):
    if checkUser(id):
        with lock:
            return copy.deepcopy(users[id])
    else:
        logger.critical("User not found.")


def addUser(id: str, data: dict):
    if checkUser(id):
        deleteUser(id)
    with lock:
        users[id] = data
        if data["mode"] == "pincode":
            if data["pincode"] not in search_data["pincode"]:
                search_data["pincode"][data["pincode"]] = [id]
            else:
                search_data["pincode"][data["pincode"]].append(id)
        elif data["mode"] == "district":
            if data["district_id"] not in search_data["district"]:
                search_data["district"][data["district_id"]] = [id]
            else:
                search_data["district"][data["district_id"]].append(id)


def deleteUser(id: str):
    if checkUser(id):
        with lock:
            try:
                if users[id]["mode"] == "pincode":
                    search_data["pincode"][users[id]["pincode"]].remove(id)
                elif users[id]["mode"] == "district":
                    search_data["district"][users[id]
                                            ["district_id"]].remove(id)
            except:
                logger.critical("Entry not found in search_data")
            users.pop(id, None)


def getSearch():
    with lock:
        return copy.deepcopy(search_data)


# TODO add call mode

"""
users = {
    "id": {
        "mode": pincode/district,
        "call_mode": True,
        "name": name,
        "phone": phone,
        "age": age
        params: variable type
    }
}


states = {
    "state_name": {
        "state_id": id,
        "districts": {
            "district_name": "district_id"
        }
    }
}

search = {
    "pin": [userids searching with pin]
    "district": [userids searching with district]
}

"""
