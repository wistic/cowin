from requests.sessions import DEFAULT_REDIRECT_LIMIT
from telegram import user
from cowin import getStates, getDistricts
import re

states = getStates()
users = {}


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
    if "districts" not in states[state]:
        states[state]["districts"] = getDistricts(states[state]["state_id"])
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


def checkUser(id: str):
    if id in users:
        return True
    return False


def getUser(id: str):
    return users[id]


def addUser(id: str, mode: str, params: dict):
    users[id] = {
        "mode": mode,
        "params": params
    }


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
    "pin": [userids searhcing with pin]
    "district": [userids searching with district]
}

"""


# TODO add mutex and update addUser method
