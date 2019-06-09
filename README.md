# Anaconda: Tic-Tac-Toe Coding Challenge

Eventsourced solution to Anaconda tic-tac-toe challenge.

## Technological Stack

* Python 3.7
* Falcon
* pytest

## How to run

If you want to run tests:

```sh
make test
```

If you want to run dev server (gunicorn with `--reload`):

```sh
make run-dev
```

Application will start at port 8080

## API

* `GET /api/games`: Return a list of the Games known to the server, as JSON.

Response:

```json
{
  "<uuid>": {
    "state": "<PENDING|PLAYABLE|FINISHED>",
    "players": ["alice", "bob"],
    "board": [
      [0, 1, null],
      [0, 1, null],
      [null, null, null]
    ],
    "winner": null
  }
}
```

* `POST /api/games`: Create a new Game, assigning it an ID and returning the newly created Game ID.

Request:

```json
{
  "board_side": 2
}
```

Response:

```json
{
  "id": "<uuid>"
}
```

* `GET /api/games/<id>`: Retrieve a Game by its ID, returning a 404 status code if no game with that ID exists.

Response:

```json
{
    "state": "<PENDING|PLAYABLE|FINISHED>",
    "players": ["alice", "bob"],
    "board": [
      [0, 1, null],
      [0, 1, null],
      [null, null, null]
    ],
    "winner": null
}
```

* `POST /api/games/<id>`: Join or make the move in the Game with the given ID.

Initial join request:

```json
{
  "player": "alice"
}
```

Move request:

```json
{
  "player": "alice",
  "cell": {
    "row": 0,
    "col": 0
  }
}
```


