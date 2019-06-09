import json
from functools import partial

import falcon
from falcon import media

from tictactoe.event.store import Eventstore
from tictactoe.api.resource import GamesResource, GamesProjection
from tictactoe.util.media import DataclassJSONEncoder


def create_api():
    store = Eventstore()

    projection = GamesProjection()
    store.attach(projection.handle)

    games = GamesResource(store, projection)

    json_handler = media.JSONHandler(
        dumps=partial(json.dumps, cls=DataclassJSONEncoder)
    )

    media_handlers = {falcon.MEDIA_JSON: json_handler}

    api = falcon.API()

    api.req_options.media_handlers.update(media_handlers)
    api.resp_options.media_handlers.update(media_handlers)

    api.add_route("/api/games", games)
    api.add_route("/api/games/{game_id}", games, suffix="single")

    return api
