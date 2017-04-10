import time


sessions = {}


def find_or_create_session(id_):
    """
    This function returns the client session with Wit context included if one
    exists, or it returns a newly created session

    :param id_: A Facebook ID
    :return: str
    """
    new_session = False
    session_id = ""

    # search the global sessions for the given Facebook ID
    for key in sessions.iterkeys():
        if sessions[key]["id"] == id_:
            session_id += key

    # if no session exists, let's create one
    if session_id is "":
        new_session = True
        # the session is created by taking th current epoch time in seconds,
        # and concatenating the given Facebook ID
        session_id += str(int(time.time())) + id_
        sessions[session_id] = {
            "id": id_,
            "context": {}
        }

    return session_id, new_session


def main():
    pass


if __name__ == "__main__":
    main()
