from wit import Wit
from scraper import advisory_country
from session import FacebookBotRedisSessionManager
from send import send_message, send_attachment
from debug import logger
import os
import redis


redis_store = redis.from_url(os.environ.get("REDIS_URL"))
session_manager = FacebookBotRedisSessionManager(redis_store)


ACCESS_TOKEN = os.environ["WIT_API_KEY"]


def send(session_id, country):
    """
    This function sends messages from Wit to Messenger.

    :param session_id:
    :param country:
    :return: True
    """
    id_ = session_manager.get_session(session_id)["id"]

    # check if the country is missing
    if country is None:

        # at some point, I should add the text to the context in get_travel_advisory so I can access it here
        ###
        logger.error("{}, Country: Missing".format(id_))
        ###

        send_message(id_, "Where? I'm still getting the hang of this. Try and make sure the country is spelled correctly.")
    else:

        ###
        logger.info("{}, Country: {}".format(id_, country))
        ###

        # get advisory
        advisory = advisory_country(country)

        # prepare image
        image = "static/adv-cat-{}.png".format(advisory["advisory_code"])
        indicator = "This is a category {} warning (out of 4)".format(advisory["advisory_code"])
        url = "https://travel.gc.ca{}".format(advisory["url"])

        send_attachment(id_, "{}: {}".format(country, advisory["advisory"]), indicator, image, url)

    return True


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


def handle_message(response, session_id):
    """
    This function handles all text responses

    :param response: A Wit response context
    :param session_id
    :return: None
    """
    # get all entities
    entities = response["entities"]
    # see if country entity present
    country = first_entity_value(entities, "country")

    send(session_id, country)


def create_client():
    return Wit(access_token=ACCESS_TOKEN)


def main():
    pass


if __name__ == "__main__":
    main()
