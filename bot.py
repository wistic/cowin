import os

from logger import logger
from telegram.ext.messagehandler import MessageHandler
from database import checkUser, deleteUser, getDistrictCode, getDistrictName, getStateCode, getStateName, addUser

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, CallbackQueryHandler, Filters


def getKeyboard(mode: str):
    if mode == "start":
        keyboard = [
            [InlineKeyboardButton("Register", callback_data="1_register")],
            [InlineKeyboardButton("Delete my data", callback_data="1_delete")]
        ]
        text = "Register to receive updates when vaccination slots are available. Choose an option:"
        return text, InlineKeyboardMarkup(keyboard)
    elif mode == "existing_user":
        keyboard = [
            [InlineKeyboardButton("Yes, Modify",
                                  callback_data="2_modify")],
            [InlineKeyboardButton("No, Cancel",
                                  callback_data="2_cancel")]
        ]
        text = "You have already registered with us. Do you want to modify your data?"
        return text, InlineKeyboardMarkup(keyboard)
    elif mode == "mode_select":
        keyboard = [
            [InlineKeyboardButton("Search by pin", callback_data="3_pin")],
            [InlineKeyboardButton("Search by district",
                                  callback_data="3_district")]
        ]
        text = "Select the mode for search:"
        return text, InlineKeyboardMarkup(keyboard)


def getDynamicKeyboard(mode: str, array: list):
    text = "Is your "+mode+" any of these?"
    keyboard = [
        [InlineKeyboardButton(entry, callback_data=(mode+"_"+entry))] for entry in array
    ]
    keyboard.append([InlineKeyboardButton(
        "None of these", callback_data=(mode+"_None"))])
    return text, InlineKeyboardMarkup(keyboard)


def start(update: Update, context: CallbackContext):
    if "first_time" not in context.user_data:
        update.message.reply_text("Hi "+update.effective_user.full_name+"!")
        update.message.reply_text("👋")
        context.user_data["first_time"] = True
    context.user_data.pop("state", None)
    context.user_data.pop("data_mode", None)
    context.user_data.pop("pincode", None)
    context.user_data.pop("district", None)
    context.user_data["back_status"] = "start"
    text, keyboard = getKeyboard("start")
    update.message.reply_text(text, reply_markup=keyboard)


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    id = str(update.effective_chat.id)

    if query.data == "1_register":
        if checkUser(id):
            text, keyboard = getKeyboard("existing_user")
        else:
            text, keyboard = getKeyboard("mode_select")
        query.edit_message_text(text, reply_markup=keyboard)
    elif query.data == "1_delete":
        context.user_data["back_status"] = "start"
        context.user_data.pop("state", None)
        context.user_data.pop("data_mode", None)
        context.user_data.pop("pincode", None)
        context.user_data.pop("district", None)
        if checkUser(id):
            deleteUser(id)
            query.edit_message_text(
                "Data successfully deleted. If you want to register again, send /start.")
        else:
            query.edit_message_text(
                "No data found. If you want to register, send /start.")
    elif query.data == "2_modify":
        text, keyboard = getKeyboard("mode_select")
        query.edit_message_text(text, reply_markup=keyboard)
    elif query.data == "2_cancel":
        query.edit_message_text(
            "👌You will receive a message whenever slots are available.")
    elif query.data == "3_pin":
        context.user_data["back_status"] = "mode_select"
        context.user_data["data_mode"] = "pincode"
        query.edit_message_text(
            "Ok. Send me the pincode of your region. Else send /back to go back.")
    elif query.data == "3_district":
        context.user_data["back_status"] = "mode_select"
        context.user_data["data_mode"] = "state"
        query.edit_message_text(
            "Ok. Send me the name of your state. Else send /back to go back.")
    else:
        if query.data.startswith("state") and "data_mode" in context.user_data and context.user_data["data_mode"] == "state":
            state_name = query.data.split("_", 1)[-1]
            if state_name == "None":
                query.edit_message_text(
                    "Ok. Send me the name of your state again. Else send /back to go back.")
            else:
                text = "Selected state: *"+state_name + \
                    "*\n\nNow, enter the name of you district. Else, send /back to go back."
                context.user_data["data_mode"] = "district"
                context.user_data["state"] = state_name
                query.edit_message_text(text, parse_mode="markdown")
        elif query.data.startswith("district") and "data_mode" in context.user_data and context.user_data["data_mode"] == "district":
            district = query.data.split("_", 1)[-1]
            if district == "None":
                query.edit_message_text(
                    "Ok. Send me the name of your district again. Else send /back to go back.")
            else:
                text = "Selected district: *"+district + \
                    "*\n\nNow tell me you age. Else send /back to go back."
                context.user_data["data_mode"] = "age"
                context.user_data["district"] = district
                query.edit_message_text(text, parse_mode="markdown")


def back(update: Update, context: CallbackContext):
    if "back_status" not in context.user_data:
        update.message.reply_text(
            "Can't go back. Send /start to start over again.")
    else:
        text, keyboard = getKeyboard(context.user_data["back_status"])
        context.user_data["back_status"] = "start"
        context.user_data.pop("state", None)
        context.user_data.pop("data_mode", None)
        context.user_data.pop("pincode", None)
        context.user_data.pop("district", None)
        update.message.reply_text(text, reply_markup=keyboard)


def message(update: Update, context: CallbackContext):
    id = str(update.effective_chat.id)
    if "data_mode" not in context.user_data:
        update.message.reply_text("Didn't get ya. Please /start over again.")
    else:
        if context.user_data["data_mode"] == "pincode":
            try:
                pincode = int(update.message.text)
            except:
                update.message.reply_text(
                    "Invalid pincode. Please enter again.")
            else:
                if len(str(pincode)) != 6 or str(pincode)[0] == "0":
                    update.message.reply_text(
                        "Invalid pincode. Please enter again.")
                else:
                    context.user_data["data_mode"] = "age"
                    context.user_data["pincode"] = pincode
                    update.message.reply_text(
                        "Ok. Now tell me your age. Else send /back to go back.")
        elif context.user_data["data_mode"] == "state":
            state = getStateName(update.message.text)
            if state is None:
                update.message.reply_text(
                    "*\"{}\"* not matching with name of any state. Please enter again.".format(update.message.text), parse_mode="markdown")
            elif isinstance(state, list):
                text, keyboard = getDynamicKeyboard("state", state)
                update.message.reply_text(text, reply_markup=keyboard)
            elif isinstance(state, str):
                text = "Selected state: *"+state + \
                    "*\n\nNow, enter the name of you district. Else, send /back to go back."
                context.user_data["data_mode"] = "district"
                context.user_data["state"] = state
                update.message.reply_text(text, parse_mode="markdown")
        elif context.user_data["data_mode"] == "district":
            if "state" not in context.user_data:
                logger.critical("state not in user_date")
                update.message.reply_text(
                    "Sorry, some error occured. Please /start over again.")
            else:
                district = getDistrictName(
                    update.message.text, context.user_data["state"])
                if district is None:
                    update.message.reply_text(
                        "*\"{}\"* not matching with name of any district. Please enter again.".format(update.message.text), parse_mode="markdown")
                elif isinstance(district, list):
                    text, keyboard = getDynamicKeyboard("district", district)
                    update.message.reply_text(text, reply_markup=keyboard)
                elif isinstance(district, str):
                    text = "Selected district: *"+district + \
                        "*\n\nNow tell me your age. Else send /back to go back."
                    context.user_data["data_mode"] = "age"
                    context.user_data["district"] = district
                    update.message.reply_text(text, parse_mode="markdown")
        elif context.user_data["data_mode"] == "age":
            try:
                age = int(update.message.text)
            except:
                update.message.reply_text(
                    "Invalid age. Please enter again.")
            else:
                if age < 18:
                    update.message.reply_text(
                        "Sorry, currently vaccination is available only for *18+*. Send /start to register.", parse_mode="markdown")
                else:
                    if "pincode" in context.user_data:
                        data = {
                            "mode": "pincode",
                            "call_mode": False,
                            "name": update.effective_user.full_name,
                            "age": age,
                            "pincode": context.user_data["pincode"]
                        }
                        addUser(id, data)
                    elif "state" in context.user_data and "district" in context.user_data:
                        data = {
                            "mode": "district",
                            "call_mode": False,
                            "name": update.effective_user.full_name,
                            "age": age,
                            "district": context.user_data["district"],
                            "state": context.user_data["state"],
                            "state_id": getStateCode(context.user_data["state"]),
                            "district_id": getDistrictCode(context.user_data["state"], context.user_data["district"])
                        }
                        addUser(id, data)
                    else:
                        logger.critical("neither pincode not district")
                    update.message.reply_text(
                        "*Successfully registered*. Send /call if you want to receive call when slots are available.", parse_mode="markdown")
                context.user_data.pop("back_status", None)
                context.user_data.pop("state", None)
                context.user_data.pop("data_mode", None)
                context.user_data.pop("pincode", None)
                context.user_data.pop("district", None)


if __name__ == "__main__":
    updater = Updater(os.environ["COWISTICBOT"], use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler('back', back))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, message))

    updater.start_polling()
    updater.idle()


# TODO add ask phone
