from enum import Enum
from typing import Iterable

from tictactoe.board import Board, Cell
from tictactoe.error import GameError
from tictactoe.event import (
    GameEvent,
    GameCreated,
    PlayerJoined,
    PlayerMoved,
    GameStarted,
    GameFinished,
)
from tictactoe.player import Player
from tictactoe.util.method_dispatch import instance_method_dispatch


class GameState(Enum):
    PENDING = 1
    PLAYABLE = 2
    FINISHED = 3


class Game:
    MAX_PLAYERS = 2

    def __init__(self, events: Iterable[GameEvent]):
        self.changes = []
        self.board = None
        self.previous_player = None

        for event in events:
            self.apply(event)

    @classmethod
    def create(cls, board_side=3):
        """
        Create initial game aggregate with specified board side.

        >>> game = Game.create(board_side=5)
        >>> game.state.name
        'PENDING'
        """
        created = GameCreated(board_side)
        initial_events = [created]

        game = cls(initial_events)
        game.changes.extend(initial_events)
        return game

    def join(self, player: Player):
        """
        Attempt to join game by player. Idempotent action.

        >>> game = Game.create()
        >>> game.join(Player("alice"))
        >>> game.join(Player("bob"))
        >>> game.join(Player("bob"))
        >>> game.players
        [Player(name='alice'), Player(name='bob')]

        Game will be PLAYABLE as soon as there is enough players.

        >>> game.state.name
        'PLAYABLE'

        Will raise an error if maximum number of players reached and some other player attempts to join.

        >>> game.join(Player("chuck"))
        Traceback (most recent call last):
        ...
        tictactoe.error.GameError: Maximum number of players reached
        """
        if player not in self.players:
            if len(self.players) < self.MAX_PLAYERS:
                player_joined = PlayerJoined(player)
                self._handle(player_joined)

                if len(self.players) == self.MAX_PLAYERS:
                    state_changed_event = GameStarted()
                    self._handle(state_changed_event)
            else:
                raise GameError("Maximum number of players reached")

    def move(self, cell: Cell, player: Player):
        """
        Attempt to play move on game board.
        It is only possible to move if game is PLAYABLE and current player is not a player of previous move.
        """
        if not self.state == GameState.PLAYABLE:
            raise GameError("Game is not PLAYABLE")

        if player == self.previous_player:
            raise GameError("Player already moved")

        self.board.validate(cell)
        self._handle(PlayerMoved(cell, player))

        if self.board.is_winning(cell):
            self._handle(GameFinished(player))
        elif not self.board.has_available_cells:
            self._handle(GameFinished(None))

    def _handle(self, event: GameEvent):
        """
        Helper method to apply event and add it to changelist.
        """
        self.apply(event)
        self.changes.append(event)

    @instance_method_dispatch
    def apply(self, event: GameEvent):
        pass

    @apply.register(GameCreated)
    def _apply(self, event: GameCreated):
        self.players = []
        self.state = GameState.PENDING
        self.board = Board(event.board_side)

    @apply.register(PlayerJoined)
    def _apply(self, event: PlayerJoined):
        self.players.append(event.player)

    @apply.register(GameStarted)
    def _apply(self, _: GameStarted):
        self.state = GameState.PLAYABLE

    @apply.register(GameFinished)
    def _apply(self, _: GameFinished):
        self.state = GameState.FINISHED

    @apply.register(PlayerMoved)
    def _apply(self, event: PlayerMoved):
        self.board.move(event.cell, event.player)
        self.previous_player = event.player
