import requests
import os


IMAGE_ENDPOINT = "https://canadiantravelassistant-stage.herokuapp.com/{}"
FB_API_ENDPOINT = "https://graph.facebook.com/v{}/me/{}?access_token={}"
FB_API_VERSION = os.environ["FB_API_VERSION"]
FB_ACCESS_TOKEN = os.environ["FB_ACCESS_TOKEN"]


def send_message(recipient, message):
    """
    This function sends a text message to the Facebook Send API.

    :param recipient: Facebook ID
    :param message: A string
    :return: response
    """
    data = {
        "recipient": {
            "id": recipient
        },
        "message": {
            "text": message
        }
    }

    return send("messages", data)


def send_typing(recipient):
    """
    This function sends a "typing on" indicator to the Facebook Send API.

    :param recipient: Facebook ID
    :return: response
    """
    data = {
        "recipient": {
            "id": recipient
        },
        "sender_action": "typing_on"
    }

    return send("messages", data)


def send_mark_seen(recipient):
    """
    This function sends a "seen" indicator to the Facebook Send API.

    :param recipient: Facebook ID
    :return: response
    """
    data = {
        "recipient": {
            "id": recipient
        },
        "sender_action": "mark_seen"
    }

    return send("messages", data)


def send_attachment(recipient, message, submessage, image, link):
    """
    This function sends an attachment to the Facebook Send API.

    :param recipient: Facebook ID
    :param message: A message string
    :param submessage: A submessage string
    :param image: An image URL
    :return: response
    """
    data = {
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": message,
                            "subtitle": submessage,
                            "image_url": IMAGE_ENDPOINT.format(image),
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "url": link,
                                    "title": "Read More"
                                },
                                {
                                    "type": "element_share"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }

    return send("messages", data)


def define_greeting(message):
    """

    :return:
    """
    data = {
        "setting_type": "greeting",
        "greeting": {
            "text": message
        }
    }

    return send("thread_settings", data)


def define_call_to_action(message):
    """

    :return:
    """
    data = {
        "setting_type": "call_to_actions",
        "thread_state": "new_thread",
        "call_to_actions": [
            {
                "payload": message
            }
        ]
    }

    return send("thread_settings", data)


def send(platform, data):
    """
    This function makes a Facebook API POST call.

    :param platform: The desired Facebook endpoint
    :param data: A JSON object
    :return: response
    """
    u = endpoint(platform, FB_ACCESS_TOKEN)
    h = {"Content-Type": "application/json"}

    return requests.post(u, json=data, headers=h)


def endpoint(target, token):
    """
    This function generates a Facebook API endpoint URL.

    :param target: The desired Facebook platform
    :param token: Page application token string from Facebook
    :return: URL string
    """
    return FB_API_ENDPOINT.format(FB_API_VERSION, target, token)


def main():
    response = define_call_to_action("Hello").json()
    print response


if __name__ == "__main__":
    main()
