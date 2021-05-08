import requests
import json
from urllib.parse import urljoin
import datetime


def makeRequest(url: str, payload={}):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url, params=payload, headers=headers)
    if response.status_code == requests.codes.ok:
        return json.loads(response.text)


def getStates():
    url = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
    states = makeRequest(url)["states"]
    return {entry["state_name"]: {"state_id": entry["state_id"]} for entry in states}


def getDistricts(state_id: int):
    base_url = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/"
    url = urljoin(base_url, str(state_id))
    districts = makeRequest(url)["districts"]
    return {entry["district_name"]: entry["district_id"] for entry in districts}


def findbyPin(pin: int):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin"
    payload = {
        "pincode": pin,
        "date": datetime.datetime.today().strftime("%d-%m-%Y")
    }
    return makeRequest(url, payload)


def calenderbyPin(pin: int):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin"
    payload = {
        "pincode": pin,
        "date": datetime.datetime.today().strftime("%d-%m-%Y")
    }
    return makeRequest(url, payload)


def findbyDistrict(district_id: int):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"
    payload = {
        "district_id": district_id,
        "date": datetime.datetime.today().strftime("%d-%m-%Y")
    }
    return makeRequest(url, payload)


def calendarbyDistrict(district_id: int):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
    payload = {
        "district_id": district_id,
        "date": datetime.datetime.today().strftime("%d-%m-%Y")
    }
    return makeRequest(url, payload)
