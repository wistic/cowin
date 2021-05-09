import json
from logger import logger
from cowin import getStates, getDistricts
import threading
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

lock = threading.RLock()


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
    with lock:
        if checkUser(id):
            return copy.deepcopy(users[id])
        else:
            logger.critical("User not found.")


def addUser(id: str, data: dict):
    with lock:
        if checkUser(id):
            deleteUser(id)
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
    with lock:
        if checkUser(id):
            try:
                if users[id]["mode"] == "pincode":
                    search_data["pincode"][users[id]["pincode"]].remove(id)
                    if len(search_data["pincode"][users[id]["pincode"]]) == 0:
                        search_data["pincode"].pop(users[id]["pincode"])
                elif users[id]["mode"] == "district":
                    search_data["district"][users[id]
                                            ["district_id"]].remove(id)
                    if len(search_data["district"][users[id]["district_id"]]) == 0:
                        search_data["district"].pop(users[id]["district_id"])
            except:
                logger.critical("Entry not found in search_data")
            users.pop(id, None)


def getSearch():
    with lock:
        return copy.deepcopy(search_data)


def addPhone(id: str, phone: str):
    with lock:
        if checkUser(id):
            users[id]["phone"] = phone
            users[id]["call_mode"] = True


def changeCallMode(id: str, mode: bool):
    with lock:
        if checkUser(id):
            users[id]["call_mode"] = mode


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
