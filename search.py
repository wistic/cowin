import time
from logger import logger
from bot import sendMessage
from telegram import Bot
from call import callUsers
from database import getSearch, getUser
from cowin import calenderbyPin, calendarbyDistrict


def generateMessages(filtered_data: dict, age: int):
    text_arr = []
    for center in filtered_data[age].values():
        text = "*Name:* "+center["name"]+"\n*Address:* "+center["address"]+"\n*Pin code:* " + \
            str(center["pincode"])+"\n*Fee:* " + \
            center["fee_type"]+"\n\n*Sessions:*\n\n"
        for session in center["sessions"]:
            text += "*Date:* "+session["date"]+"\n*Vacancy:* " + \
                str(session["available_capacity"]) + \
                "\n*Vaccine:* "+session["vaccine"]+"\n\n"
        text_arr.append(text)

    return text_arr


def filterData(filtered_data: dict, age: int, center: dict, session: dict):
    if center["center_id"] not in filtered_data[age]:
        filtered_data[age][center["center_id"]] = {
            "name": center["name"],
            "address": center["address"],
            "pincode": center["pincode"],
            "fee_type": center["fee_type"],
            "sessions": []
        }
    session_data = {
        "date": session["date"],
        "available_capacity": session["available_capacity"],
        "vaccine": session["vaccine"]
    }
    filtered_data[age][center["center_id"]
                       ]["sessions"].append(session_data)


def count_slots(filtered_data: dict, age: int):
    slots = 0
    for center in filtered_data[age].values():
        for session in center["sessions"]:
            slots += session["available_capacity"]
    return slots


def get_filtered_data(response):
    filtered_data = {
        18: {},
        45: {}
    }
    for center in response["centers"]:
        if "sessions" in center:
            for session in center["sessions"]:
                if "available_capacity" in session and session["available_capacity"] > 0:
                    filterData(filtered_data, 45, center, session)
                    if session["min_age_limit"] == 18:
                        filterData(filtered_data, 18, center, session)
    return filtered_data


def search(bot: Bot):
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
        response = calenderbyPin(pin, 0)
        if response is None:
            break
        if not isinstance(response, dict) or "centers" not in response:
            break

        filtered_data = get_filtered_data(response)

        centers_18 = len(filtered_data[18])
        centers_45 = len(filtered_data[45])
        slots_18 = count_slots(filtered_data, 18)
        slots_45 = count_slots(filtered_data, 45)

        alert_text = "Vaccination slots available.\n\nFollowing are the details of the available slots:"
        text_arr_18 = generateMessages(filtered_data, 18)
        text_arr_45 = generateMessages(filtered_data, 45)

        for user_id in search_data["pincode"][pin]:
            user = getUser(user_id)
            greeting = "Greetings "+user["name"]+"!"
            user_age = user["age"]
            if user_age >= 45:
                if slots_45 > 0:
                    sendMessage(bot, user_id, greeting)
                    sendMessage(bot, user_id, alert_text)
                    for text in text_arr_45:
                        sendMessage(bot, user_id, text)
                    if user["call_mode"]:
                        if pin not in call_directory["pincode"]:
                            call_directory["pincode"][pin] = {}
                        if 45 not in call_directory["pincode"][pin]:
                            call_directory["pincode"][pin][45] = {
                                "slots": slots_45,
                                "centers": centers_45,
                                "users": []
                            }
                        entry = {
                            "id": user_id,
                            "name": user["name"],
                            "phone": user["phone"]
                        }
                        call_directory["pincode"][pin][45]["users"].append(
                            entry)
            else:
                if slots_18 > 0:
                    sendMessage(bot, user_id, greeting)
                    sendMessage(bot, user_id, alert_text)
                    for text in text_arr_18:
                        sendMessage(bot, user_id, text)
                    if user["call_mode"]:
                        if pin not in call_directory["pincode"]:
                            call_directory["pincode"][pin] = {}
                        if 18 not in call_directory["pincode"][pin]:
                            call_directory["pincode"][pin][18] = {
                                "slots": slots_18,
                                "centers": centers_18,
                                "users": []
                            }
                        entry = {
                            "id": user_id,
                            "name": user["name"],
                            "phone": user["phone"]
                        }
                        call_directory["pincode"][pin][18]["users"].append(
                            entry)

    for district_id in search_data["district"]:
        response = calendarbyDistrict(district_id, 0)
        if response is None:
            break
        if not isinstance(response, dict) or "centers" not in response:
            break

        district_name = response["centers"][0]["district_name"]
        filtered_data = get_filtered_data(response)

        centers_18 = len(filtered_data[18])
        centers_45 = len(filtered_data[45])
        slots_18 = count_slots(filtered_data, 18)
        slots_45 = count_slots(filtered_data, 45)

        alert_text = "Vaccination slots available.\n\nFollowing are the details of the available slots:"
        text_arr_18 = generateMessages(filtered_data, 18)
        text_arr_45 = generateMessages(filtered_data, 45)

        for user_id in search_data["district"][district_id]:
            user = getUser(user_id)
            greeting = "Greetings "+user["name"]+"!"
            user_age = user["age"]
            if user_age >= 45:
                if slots_45 > 0:
                    sendMessage(bot, user_id, greeting)
                    sendMessage(bot, user_id, alert_text)
                    for text in text_arr_45:
                        sendMessage(bot, user_id, text)
                    if user["call_mode"]:
                        if district_id not in call_directory["district"]:
                            call_directory["district"][district_id] = {}
                        if 45 not in call_directory["district"][district_id]:
                            call_directory["district"][district_id][45] = {
                                "slots": slots_45,
                                "centers": centers_45,
                                "district_name": district_name,
                                "users": []
                            }
                        entry = {
                            "id": user_id,
                            "name": user["name"],
                            "phone": user["phone"]
                        }
                        call_directory["district"][district_id][45]["users"].append(
                            entry)
            else:
                if slots_18 > 0:
                    sendMessage(bot, user_id, greeting)
                    sendMessage(bot, user_id, alert_text)
                    for text in text_arr_18:
                        sendMessage(bot, user_id, text)
                    if user["call_mode"]:
                        if district_id not in call_directory["district"]:
                            call_directory["district"][district_id] = {}
                        if 18 not in call_directory["district"][district_id]:
                            call_directory["district"][district_id][18] = {
                                "slots": slots_18,
                                "centers": centers_18,
                                "district_name": district_name,
                                "users": []
                            }
                        entry = {
                            "id": user_id,
                            "name": user["name"],
                            "phone": user["phone"]
                        }
                        call_directory["district"][district_id][18]["users"].append(
                            entry)

    callUsers(call_directory)
    del search_data
    del call_directory

    time.sleep(sleep_time)
