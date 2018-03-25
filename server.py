from flask import Flask, jsonify, render_template, redirect, request, abort, Response, flash, session
import sys
import os
import json
from twilio import twiml
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import bugsnag
from bugsnag.flask import handle_exceptions
import twilio_functions

app = Flask(__name__)
handle_exceptions(app) # bugsnag config
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "s0Then!stO0dth34ean9a11iw4n7edto9ow4s8ur$7!ntOfL*me5")
# app.jinja_env.endefined = StrictUndefined

AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
CALLER_ID = os.environ.get("TWILIO_CALLER_ID")
TWILIO_APP_SID = os.environ.get("TWILIO_TWIML_APP_SID")
ON_DUTY = os.environ.get("ON_DUTY")

bugsnag.configure(
    api_key=os.environ.get("BUGSNAG_BUGGLIO_KEY"),
    project_root="/",
)

# @app.before_request
# def limit_remote_addr():
#     if request.remote_addr != '10.20.30.40':
#         abort(403)  # Forbidden

# @app.route('/my_service', methods=['GET', 'OPTIONS'])
# @crossdomain(origin='*')
# def my_service():
#     return jsonify(foo='cross domain ftw')

@app.route("/", methods=['GET', 'POST'])
def homepage():
    """display homepage.
    """
    # build homepage, fomr to submit phone #
    return render_template("index.html")

@app.route("/bugsnag", methods=['GET', 'POST'])
def process_notif():
    """this route responds to notifications from the Bugsnag webhook.
    """
    # this app route should only accept requests from Bugsnag's IP addresses??
    # if request.remote_addr in ['104.196.245.109', '104.196.254.247']:
    data = json.loads(request.data)
    sms_msg = parse_bugsnag(data)
    # print("Bugsnag notification: {}".format(data))
    print(sms_msg)

    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        to=ON_DUTY,
        from_=CALLER_ID,
        body=sms_msg,
        # media_url="https://bugglio.herokuapp.com/static/images/dot.png",
    )

    return "OK"

    # else:
    #      abort(403)  # Forbidden

def parse_bugsnag(data):
    """accepts a dictionary of data from the JSON payload from Bugsnag's notification.
    """
    notif_type = data['trigger']['type']
    message = data['trigger']['message']
    project = data['project']['name']
    sms_msg = message + " on " + project

    if notif_type == 'exception':
        sms_msg = sms_msg + " details: " + data['error']['exceptionClass'] + " " + data['error']['message']

        # // The type of trigger sent (always present)
        # // - "firstException"         A new error is created from a new exception
        # // - "powerTen"               An error occurs frequently
        # // - "exception"              Every time an exception is received
        # // - "reopened"               An error is automatically reopened
        # // - "projectSpiking"         A spike in exception in a project has been detected
        # // - "comment"                A comment is added to an error
        # // - "errorStateManualChange" A user has manually changed the state of an error

    return sms_msg

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """this route responds to incoming texts.
    """
    resp = MessagingResponse()

    sms_msg = "Everything's perfectly all right now. We're fine. We're all fine here, now, thank you. How are you?"

    resp.message(sms_msg)

    return str(resp)

    # twiml = """
    # <Reposnse>
    #     <Message>
    #         Heyo
    #     </Message>
    # </Response>
    # """"



if __name__ == "__main__":
    bugsnag.notify(Exception("Test Error"))
    DEBUG = "NO_DEBUG" not in os.environ
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
