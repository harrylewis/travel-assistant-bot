#!bin/python

# TODO: use os.environ.get("", default) instead of os.environ[key]

from flask import (Flask, jsonify, request, make_response)
import os

from bot import create_client
from sessions import sessions, find_or_create_session
from send import send_typing, send_message
from debug import logger


app = Flask(__name__, static_folder="static")


wit = create_client()


ROOT = "/canadian_travel_advisory_bot/{}/"
FB_CALLBACK = os.environ["FB_CALLBACK_TOKEN"]
FB_VERIFY_TOKEN = os.environ["FB_VERIFICATION_TOKEN"]
FB_ACCESS_TOKEN = os.environ["FB_ACCESS_TOKEN"]


@app.route(ROOT.format(FB_CALLBACK), methods=["GET"])
def verify_token():
    # check for request type
    if request.method == "GET":
        # check for verification token
        if request.args["hub.verify_token"] == FB_VERIFY_TOKEN:

            ###
            logger.info("Validation token set matches! We're in!")
            ###

            return make_response(request.args["hub.challenge"], 200)
        else:

            ###
            logger.error("Validation token sent does not match: {}".format(request.args["hub.verify_token"]))
            ###

            return make_response("Failed validation. Make sure the validation tokens match.", 403)


@app.route(ROOT.format(FB_CALLBACK), methods=["POST"])
def webhook_callback():
    ###
    logger.info("Messaging event received.")
    ###

    data = request.json

    # ensure that callback came from a "page" object
    if data["object"] == "page":
        # go through each entry
        for entry in data["entry"]:
            # go through each messaging event
            for event in entry["messaging"]:
                # check if we have a new message
                if "message" in event:
                    print event
                    # get sender
                    sender = event["sender"]["id"]
                    # find or create session
                    session_id, new_session = find_or_create_session(sender)
                    # get message
                    message = event["message"]
                    # check to see if this is a new user/session
                    if new_session:
                        ###
                        logger.info("New session: {}".format(sender))
                        ###
                    # check to see if it is a message or attachment
                    elif "attachments" in message:

                        ###
                        logger.info("Attachment received from: {}".format(sender))
                        ###

                        # cannot process attachments
                        send_message(sender, "I can't do much with that, but if you send me a country, I can tell you what the travel advisory is for it.")
                    elif "text" in message:

                        ###
                        logger.info("Text received from: {}".format(sender))
                        ###

                        # typing...
                        send_typing(sender)
                        # converse
                        new_context = wit.run_actions(session_id, message["text"], sessions[session_id]["context"])
                        # update session
                        sessions[session_id]["context"] = new_context
                # check if we have a message delivered
                elif "delivery" in event:
                    ###
                    logger.info("Message delivered")
                    ###
                # check if we have a postback
                elif "postback" in event:
                    ###
                    logger.info("Postback")
                    ###
                else:

                    ###
                    logger.error("Unknown messaging event received.")
                    ###

    return make_response(jsonify({}), 200)


def main():
    app.run(port=5000, debug=True)


if __name__ == "__main__":
    main()
