import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from database import getUser
from logger import logger

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_phone = os.environ['TWILIO_PHONE']


def callUser(id: str, slots: int, centers: int):

    client = Client(account_sid, auth_token)

    user = getUser(id)
    if not user["call_mode"] or "phone" not in user:
        logger.critical("programming error")
        return

    response = VoiceResponse()

    response.say('नमस्ते '+user["name"] +
                 '. मैं वैक्सीन बॉट हूं.', voice='Polly.Aditi', language='hi-IN')
    response.pause(length=1)
    if user["mode"] == "pincode":
        response.say(str(slots)+' स्लॉट ',
                     voice='Polly.Aditi', language='hi-IN')
        response.say('pincode '+str(user["params"]["pincode"]),
                     voice='Polly.Aditi', language='hi-IN')
        response.say('के लिए '+str(centers)+' केंद्र में उपलब्ध हैं। अधिक जानकारी के लिए तुरंत टेलीग्राम चेक करें।',
                     voice='Polly.Aditi', language='hi-IN')
    else:
        response.say('जिला '+str(user["params"]["district"])+' के लिए '+str(centers)+' केंद्र में '+str(
            slots)+' स्लॉट उपलब्ध हैं। अधिक जानकारी के लिए तुरंत टेलीग्राम चेक करें।', voice='Polly.Aditi', language='hi-IN')

    client.calls.create(
        twiml=str(response),
        to=user["phone"],
        from_=twilio_phone
    )


# TODO only initialize client once
