#!bin/python

# TODO: use os.environ.get("", default) instead of os.environ[key]
# TODO: Current "behavioural bug" where greeting only appears once, when user
# TODO: FIRST interacts with the page. That's fine, I thought it was if there
# TODO: was a session or not, but that is just on my side. In my code, if no
# TODO: session is present, it just returns, because I thought this would go
# TODO: straight to a greeting. Have to figure out a way around this. If there
# TODO: is a flag to know whether it is a new message connection or not, that
# TODO: would be good, otherwise, hopefully just the fact that redis has the
# TODO: session stored is good enough. Not really expecting down time on it.

# NOTE: Greeting only appears once! Once for on each new page access token, for
# every NEW messenger connection. Ideally since the page access token should
# never change, it should be eternally once.

from flask import (Flask, jsonify, request, make_response)
import os
import redis
import ast

from bot import create_client
from send import send_typing, send_message, send_mark_seen
from debug import logger
from session import FacebookBotRedisSessionManager


app = Flask(__name__, static_folder="static")

redis_store = redis.from_url(os.environ.get("REDIS_URL"))
session_manager = FacebookBotRedisSessionManager(redis_store)
wit = create_client()


ROOT = "/canadian_travel_advisory_bot/{}/"
FB_CALLBACK = os.environ["FB_CALLBACK_TOKEN"]
FB_VERIFY_TOKEN = os.environ["FB_VERIFICATION_TOKEN"]
FB_ACCESS_TOKEN = os.environ["FB_ACCESS_TOKEN"]


@app.route("/")
def root():
    return "Canadian Travel Assistant"


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
    logger.info("MESSAGING EVENT RECEIVED.")
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

                    ###
                    logger.info("MESSAGE RECEIVED.")
                    ###

                    # get sender
                    sender = event["sender"]["id"]
                    # get session token
                    token = session_manager.get_session_token(sender)
                    # try and find session
                    existing_session = session_manager.get_session(token)
                    # get message
                    message = event["message"]
                    # check to see if this is a new user/session
                    if existing_session is None:
                        ###
                        logger.info("New session: {}".format(sender))
                        ###

                        # mark seen
                        send_mark_seen(sender)

                        session_manager.create_session(sender, **{
                            "context": {},
                            "lang": 0
                        })
                    # check to see if it is a message or attachment
                    elif "attachments" in message:

                        ###
                        logger.info("Attachment received from: {}".format(sender))
                        ###

                        # typing...
                        send_typing(sender)
                        # cannot process attachments
                        send_message(sender, "I can't do much with that, but if you send me the name of a country, I can tell you the travel advisory for it.")
                    elif "text" in message:

                        ###
                        logger.info("Text received from: {}".format(sender))
                        ###

                        # typing...
                        send_typing(sender)
                        # get session ID
                        session_id = session_manager.get_session_token(sender)
                        # converse
                        new_context = wit.run_actions(session_id, message["text"], ast.literal_eval(existing_session["context"]))
                        # update session
                        session_manager.update_session(sender, **{
                            "context": new_context
                        })
                # check if we have a message delivered
                elif "delivery" in event:
                    ###
                    logger.info("MESSAGE DELIVERED.")
                    ###
                # check if a message was read
                elif "read" in event:
                    ###
                    logger.info("MESSAGE READ.")
                    ###
                # check if we have a postback
                elif "postback" in event:
                    ###
                    logger.info("POSTBACK RECEIVED.")
                    ###

                    # get sender
                    sender = event["sender"]["id"]
                    # get postback data
                    postback = event["postback"]
                    payload = postback["payload"]
                    # what do I do?
                    if payload == "WHAT_DO_I_DO":
                        # typing...
                        send_typing(sender)
                        # cannot process attachments
                        send_message(sender, "I want you to help you stay informed when travelling abroad. Ask me something like \"What is the current travel advisory for the Brazil?\".")
                else:

                    ###
                    logger.error("UKNOWN MESSAGING EVENT.")
                    ###

    return make_response(jsonify({}), 200)


def main():
    app.run(port=5000, debug=True)


if __name__ == "__main__":
    main()
