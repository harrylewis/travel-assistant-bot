import time
import hashlib
import redis


class FacebookBotRedisSessionManager(object):
    """
    This class is used to manage the Facebook Bot user sessions on a Redis
    instance. One instance should be created and used to manage all of the
    Redis interactions.

    Args:
        url - A URL string representing the location of the active Redis
            instance.

    Attributes:
        _hash_algorithm - The class-wide hashing algorithm used to hash the
            user-bot IDs into session tokens.
        _ds - A Redis instance, to be used for all redis instance
            accessed through the python interface. It should be accessed
            through the ds property.

    High Level Usage:
        manager = RedisSessionManager(redis_datastore)
        session = manager.create_session(fb_id)
    """

    _hash_algorithm = hashlib.sha224

    def __init__(self, ds):
        self._ds = ds

    def create_session(self, id_, **kwargs):
        """
        This function is used to create a new session for a particular user.
        The user is identified by the user id provided. The session are
        currently constructed using user id provided, and the current time.
        The token used to associate the user with the session is created using
        the internal _generate_session_token method.

        :param id_: A string representing the unique user-bot relationship, to
            used to create the unique session.
        :return: session object
        """
        token = self._generate_session_token(id_)
        # set redis hash - required
        self.ds.hset(token, "id", id_)
        self.ds.hset(token, "c_at", time.time())
        self.ds.hset(token, "u_at", time.time())
        # optional
        for key, value in kwargs.iteritems():
            self.ds.hset(token, key, value)

        return self.ds.hgetall(token)

    def update_session(self, id_, **kwargs):
        """
        This function is used to update field in a session object given a
        particular user-bot ID.

        :param id_: A string representing the unique user-bot relationship, to
            used to create the unique session.
        :param kwargs: A dictionary representing the fields to modify.
        :return: 1/0 (success/error)
        """
        token = self.get_session_token(id_)
        # update redis hash values
        for key, value in kwargs.iteritems():
            self.ds.hset(token, key, value)
        # updated now
        self.ds.hset(token, "u_at", time.time())

        return self.ds.hgetall(token)

    def delete_session(self, id_):
        """
        This function is used to delete a particular session given a user-bot
        ID.

        :param id_: A string representing the unique user-bot relationship, to
            used to create the unique session.
        :return: 1/0 (success/error)
        """
        token = self.get_session_token(id_)

        return self.ds.delete(token)

    # Note that all of these methods MAY contain security issues because the
    # session token is created from the user-bot ID, and not in a separate
    # process. This means that ANYONE can supply the user-bot ID, and have
    # access to the session. Note though, that no personal/private/critical
    # information is being stored in the session. While this doesn't
    def get_session(self, token):
        """
        This function is used to return a session object from the redis
        instance given a particular session token.

        :param token: A string representing the session token for the session.
        :return: session object
        """
        if self.ds.exists(token):
            return self.ds.hgetall(token)
        return None

    def get_session_token(self, id_):
        """
        This function is used to retrieve the session token associated with a
        particular user. This is done by simply implementing the session token
        generating method. This merely calls _generate_session_token, but it
        allows for some separation at a higher level.

        :param id_: A string representing the unique user-bot relationship, to
            used to create the unique session.
        :return: token
        """
        return self._generate_session_token(id_)

    def _generate_session_token(self, id_):
        """
        This function is used to generate a session token in redis by hashing
        the id_ using the SHA224 algorithm 3 times recursively.

        :param id_: A string representing the unique user-bot relationship, to
            used to create the unique session.
        :return: token
        """
        a = self._hash_algorithm(id_).hexdigest()
        b = self._hash_algorithm(a).hexdigest()
        c = self._hash_algorithm(b).hexdigest()

        return c

    @property
    def ds(self):
        return self._ds


def main():
    ds = redis.from_url("redis://localhost:6379/0")
    print ds.keys()


if __name__ == "__main__":
    main()
