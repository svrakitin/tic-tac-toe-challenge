import pytest

from tictactoe.board import Cell
from tictactoe.error import GameError, GameValueError
from tictactoe.event import GameFinished, PlayerMoved
from tictactoe.game import Game, GameState


def test_cannot_move_during_pending_game(players):
    with pytest.raises(GameError, match=r"not PLAYABLE"):
        game = Game.create(board_side=1)

        game.move(Cell(0, 0), players[0])


def test_can_move_when_game_is_playable(players):
    game = Game.create(board_side=2)

    for player in players:
        game.join(player)

    game.move(Cell(0, 0), players[0])

    assert game.changes[-1] == PlayerMoved(Cell(0, 0), players[0])


def test_cannot_move_twice(players):
    game = Game.create(board_side=2)

    for player in players:
        game.join(player)

    game.move(Cell(0, 0), players[0])

    with pytest.raises(GameError, match=r"already moved"):
        game.move(Cell(0, 1), players[0])


def test_player_can_win_the_game(players):
    game = Game.create(board_side=2)

    for player in players:
        game.join(player)

    game.move(Cell(0, 0), players[0])
    game.move(Cell(0, 1), players[1])
    game.move(Cell(1, 0), players[0])

    assert game.changes[-1] == GameFinished(winner=players[0])
    assert game.state == GameState.FINISHED


def test_game_can_draw(players):
    game = Game.create(board_side=3)

    for player in players:
        game.join(player)

    game.move(Cell(0, 1), players[0])
    game.move(Cell(0, 0), players[1])
    game.move(Cell(1, 1), players[0])
    game.move(Cell(2, 1), players[1])
    game.move(Cell(1, 2), players[0])
    game.move(Cell(1, 0), players[1])
    game.move(Cell(2, 0), players[0])
    game.move(Cell(0, 2), players[1])
    game.move(Cell(2, 2), players[0])

    assert game.changes[-1] == GameFinished(winner=None)
    assert game.state == GameState.FINISHED


def test_cannot_move_out_of_board_bounds(players):
    game = Game.create(board_side=1)

    for player in players:
        game.join(player)

    with pytest.raises(GameValueError, match=r"out of bounds"):
        game.move(Cell(1, 1), players[0])


def test_cannot_move_using_unavailable_cell(players):
    game = Game.create(board_side=2)

    for player in players:
        game.join(player)

    game.move(Cell(0, 0), players[0])

    with pytest.raises(GameError, match=r"unavailable"):
        game.move(Cell(0, 0), players[1])


@pytest.mark.parametrize("board_side", [0, -1])
def test_cannot_create_game_with_incorrect_board_side(board_side):
    with pytest.raises(GameValueError):
        Game.create(board_side=board_side)
