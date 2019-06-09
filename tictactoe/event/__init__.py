from dataclasses import dataclass
from typing import Optional

from tictactoe.board import Cell
from tictactoe.player import Player


class GameEvent:
    pass


@dataclass
class GameCreated(GameEvent):
    board_side: int


@dataclass
class PlayerJoined(GameEvent):
    player: Player


@dataclass
class PlayerMoved(GameEvent):
    cell: Cell
    player: Player


@dataclass
class GameStarted(GameEvent):
    pass


@dataclass
class GameFinished(GameEvent):
    winner: Optional[Player]
