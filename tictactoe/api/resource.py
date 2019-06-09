from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid4

import falcon

from tictactoe.board import Cell
from tictactoe.event import (
    GameEvent,
    GameCreated,
    GameStarted,
    GameFinished,
    PlayerJoined,
    PlayerMoved,
)
from tictactoe.game import Game, GameState
from tictactoe.player import Player
from tictactoe.util.method_dispatch import instance_method_dispatch


@dataclass
class GameView:
    board: List[List[Optional[int]]]
    players: List[Player] = field(default_factory=list)
    state: str = GameState.PENDING.name
    winner: Optional[str] = None


class GamesProjection:
    def __init__(self):
        self.views = {}

    @instance_method_dispatch
    def handle(self, event: GameEvent, game_id):
        pass

    @handle.register(GameCreated)
    def _handle(self, event: GameCreated, game_id):
        board = []

        for _ in range(event.board_side):
            row = [None] * event.board_side
            board.append(row)

        view = GameView(board)
        self.views[game_id] = view

    @handle.register(GameStarted)
    def _handle(self, event: GameStarted, game_id):
        view = self.views[game_id]
        view.state = GameState.PLAYABLE.name

    @handle.register(GameFinished)
    def _handle(self, event: GameFinished, game_id):
        view = self.views[game_id]
        view.state = GameState.FINISHED.name

        if event.winner is not None:
            view.winner = event.winner.name

    @handle.register(PlayerJoined)
    def _handle(self, event: PlayerJoined, game_id):
        view = self.views[game_id]
        view.players.append(event.player.name)

    @handle.register(PlayerMoved)
    def _handle(self, event: PlayerMoved, game_id):
        view = self.views[game_id]
        player_index = view.players.index(event.player.name)
        view.board[event.cell.row][event.cell.col] = player_index


class GamesResource:
    DEFAULT_BOARD_SIDE = 3

    def __init__(self, store, projection):
        self.store = store
        self.projection = projection

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        game_id = str(uuid4())

        board_side = (
            req.media.get("board_side")
            if req.media is not None
            else self.DEFAULT_BOARD_SIDE
        )

        created = Game.create(board_side=board_side)

        self.store.sink(game_id, created.changes)

        resp.media = {"id": game_id}
        resp.status = falcon.HTTP_CREATED

    def on_post_single(self, req: falcon.Request, resp: falcon.Response, game_id):
        if game_id not in self.store:
            raise falcon.HTTPNotFound(
                title="Game not found", description=f"Game with id={game_id} not found"
            )

        stream = self.store.stream(game_id)

        game = Game(stream)

        player_name = req.media.get("player")
        player = Player(player_name)

        if player not in game.players:
            game.join(player)
        else:
            media_cell = req.media.get("cell")
            cell = Cell(media_cell["row"], media_cell["col"])

            game.move(cell, player)

        self.store.sink(game_id, game.changes)

        resp.status = falcon.HTTP_ACCEPTED

    def on_get(self, _: falcon.Request, resp: falcon.Response):
        resp.media = self.projection.views

    def on_get_single(self, _: falcon.Request, resp: falcon.Response, game_id):
        if game_id not in self.projection.views:
            raise falcon.HTTPNotFound(
                title="Game not found", description=f"Game with id={game_id} not found"
            )

        resp.media = self.projection.views[game_id]
