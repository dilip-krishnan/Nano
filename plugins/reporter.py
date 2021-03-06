import sys
import logging
import traceback
from discord import errors, Message, Member, User, Server
from data.utils import log_to_file


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Reporter:
    def __init__(self, **kwargs):
        pass

    @staticmethod
    async def on_error(event, *args, **kwargs):
        e_type, value, _ = sys.exc_info()

        # Ignore Forbidden errors (but log them anyways)
        if e_type == errors.Forbidden:
            log.warning("Forbidden 403")

            if isinstance(args[0], Message):
                log_to_file("Forbidden 403. Server: {}, channel: {}".format(args[0].server, args[0].channel))

            elif isinstance(args[0], Member):
                log_to_file("Forbidden 403. Server: {}, member: {}:{}".format(args[0].server, args[0].name, args[0].id))

            else:
                try:
                    items = args[0].__dict__
                except AttributeError:
                    items = args[0].__slots__

                log_to_file("Forbidden 403. Unknown instance: {}:{}".format(type(args[0]), items))

        elif e_type == errors.HTTPException and str(value).startswith("BAD REQUEST"):
            log.warning("Bad Request 400")
            log_to_file("Bad Request 400: \nTraceback: {}".format(kwargs), "bug")

        elif e_type == errors.NotFound:
            log.warning("Not Found 404")
            log_to_file("Not Found 404: {}".format(value))

        else:
            if isinstance(args[0], (User, Member)):
                readable = "{}:{}".format(args[0].name, args[0].id)
            elif isinstance(args[0], Message):
                readable = "'{}' by {}".format(args[0].content, args[0].author.name)
            elif isinstance(args[0], Server):
                readable = "{} (server)({})".format(args[0].name, args[0].id)
            else:
                try:
                    readable = "__dict__ of {}: ".format(type(args[0]), args[0].__dict__)
                except AttributeError:
                    readable = "__slots__ of {}: ".format(type(args[0]), args[0].__slots__)

            log_to_file("EXCEPTION in {}: {}".format(event, readable), "bug")

            exc = traceback.format_exc()
            log_to_file(exc, "bug")

            log.warning("New exception, see bugs.txt")



class NanoPlugin:
    name = "Bug Reporter"
    version = "0.1"

    handler = Reporter
    events = {
        "on_error": 9,
    }
