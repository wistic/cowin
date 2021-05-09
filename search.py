import time
from logger import logger
from database import getSearch, getUser
from cowin import calenderbyPin, calendarbyDistrict


def search():
    search_data = getSearch()
    # API limit 100 calls per 5 minutes
    # We will search only for next 7 days considering the fact that vaccines are in shortage

    count = len(search_data["pincode"]) + len(search_data["district"])
    if count == 0:
        del search_data
        return

    frequency = 100//count
    sleep_time = 300//frequency

    call_directory = {
        "pincode": {},
        "district": {}
    }

    for pin in search_data["pincode"]:
        results = calenderbyPin(pin, 0)
        logger.debug(results)

    for district_id in search_data["district"]:
        results = calendarbyDistrict(district_id, 0)
        logger.debug(results)

    del search_data
    del call_directory

    time.sleep(sleep_time)
