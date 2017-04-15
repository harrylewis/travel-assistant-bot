from wit import Wit
from scraper import advisory_country
from session import FacebookBotRedisSessionManager
from send import send_message, send_attachment
from debug import logger
import os
import redis
import ast


redis_store = redis.from_url("redis://localhost:6379/0")
session_manager = FacebookBotRedisSessionManager(redis_store)


ACCESS_TOKEN = os.environ["WIT_API_KEY"]


def send(request, response):
    """
    This function sends messages from Wit to Messenger.

    :param request: The request
    :param response: The response
    :return: True
    """
    context = request["context"]
    id_ = session_manager.get_session(request["session_id"])["id"]

    # check if the country is missing
    if "country_missing" in context and context["country_missing"]:

        # at some point, I should add the text to the context in get_travel_advisory so I can access it here
        ###
        logger.error("{}, Country: Missing".format(id_))
        ###

        send_message(id_, response["text"])
    else:

        ###
        logger.info("{}, Country: {}".format(id_, context["country"]))
        ###

        # prepare image
        image = "static/adv-cat-{}.png".format(context["advisory_code"])
        indicator = "This is a category {} warning (out of 4)".format(context["advisory_code"])
        url = "https://travel.gc.ca{}".format(context["url"])

        send_attachment(id_, response["text"], indicator, image, url)

    return True


def get_travel_advisory(request):
    """
    This function updates the context with a country advisory, or a country
    missing flag.

    :param request: The request sent by the client
    :return: updated context
    """
    context = request["context"]
    entities = request["entities"]

    country = first_entity_value(entities, "country")

    if country:
        # ladies and gentlemen, we have a country, so let's get the advisory
        advisory = advisory_country(country)
        # remove certain entities
        context = remove_entities(context, ["country_missing"])
        # set the advisory values
        context["country"] = advisory["name"]
        context["advisory"] = advisory["advisory"]
        context["advisory_code"] = advisory["advisory_code"]
        context["url"] = advisory["url"]
    else:
        # no country found, remove certain entities
        context = remove_entities(context, ["advisory", "country", "advisory_code"])
        context["country_missing"] = True

    return context


def clear_session(request):
    """

    :param request:
    :return:
    """
    return {}


def first_entity_value(entities, entity):
    """
    This function returns the first entity value if the entity exists.

    :param entities: A group of entities
    :param entity: The desired entity
    :return: entity value or None
    """
    if entity not in entities:
        return None

    value = entities[entity][0]["value"]

    if not value:
        return None

    return value["value"] if isinstance(value, dict) else value


def remove_entities(context, entities):
    """
    This function removes the keys "entities" from the context.

    :param context: A Wit context
    :param entities: A list of strings/entities
    :return: updated context
    """
    for entity in entities:
        if context.get(entity) is not None:
            del context[entity]

    return context


actions = {
    "send": send,
    "get_travel_advisory": get_travel_advisory,
    "clear_session": clear_session
}


def create_client():
    return Wit(access_token=ACCESS_TOKEN, actions=actions)


def main():
    pass


if __name__ == "__main__":
    main()
