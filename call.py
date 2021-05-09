import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from database import changeCallMode
from logger import logger

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_phone = os.environ['TWILIO_PHONE']


def callUsers(call_directory: dict):
    client = Client(account_sid, auth_token)
    logger.info("started calling")

    for pin in call_directory["pincode"]:
        slots = str(call_directory["pincode"][pin]["slots"])
        centers = str(call_directory["pincode"][pin]["centers"])
        for user in call_directory["pincode"][pin]["users"]:
            id = user["id"]
            name = user["name"]
            phone = user["phone"]

            response = VoiceResponse()
            response.say('नमस्ते '+name +
                         '. मैं वैक्सीन बॉट हूं.', voice='Polly.Aditi', language='hi-IN')
            response.pause(length=1)
            response.say(slots+' स्लॉट ',
                         voice='Polly.Aditi', language='hi-IN')
            response.say('pincode '+str(pin),
                         voice='Polly.Aditi', language='hi-IN')
            response.say('के लिए '+centers+' केंद्र में उपलब्ध हैं। अधिक जानकारी के लिए तुरंत टेलीग्राम चेक करें।',
                         voice='Polly.Aditi', language='hi-IN')

            client.calls.create(
                twiml=str(response),
                to=phone,
                from_=twilio_phone
            )

            changeCallMode(id, False)

    for district_id in call_directory["district"]:
        slots = str(call_directory["district"][district_id]["slots"])
        centers = str(call_directory["district"][district_id]["centers"])
        district_name = call_directory["district"][district_id]["district_name"]
        for user in call_directory["district"][district_id]["users"]:
            id = user["id"]
            name = user["name"]
            phone = user["phone"]

            response = VoiceResponse()
            response.say('नमस्ते '+name +
                         '. मैं वैक्सीन बॉट हूं.', voice='Polly.Aditi', language='hi-IN')
            response.pause(length=1)
            response.say('जिला '+district_name+' के लिए '+centers+' केंद्र में ' + slots +
                         ' स्लॉट उपलब्ध हैं। अधिक जानकारी के लिए तुरंत टेलीग्राम चेक करें।', voice='Polly.Aditi', language='hi-IN')

            client.calls.create(
                twiml=str(response),
                to=phone,
                from_=twilio_phone
            )

            changeCallMode(id, False)

    logger.info("finished calling")


"""

call_directory = {
    "pincode" :{
        pin1 :{
            slots: 123
            centers: 123
            users: [
                {
                    id: id
                    name: name,
                    phone: phone
                }
            ]
        }
    }
    district: {
        district_id: {
            slots: 123
            centers: 123
            district_name: name
            users: [
                {
                    id: id
                    name: name,
                    phone: phone
                }
            ]
        }
    }
}

"""
