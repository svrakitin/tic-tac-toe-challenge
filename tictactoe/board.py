from dataclasses import dataclass
from tictactoe.player import Player
from tictactoe.error import GameError, GameValueError


@dataclass(frozen=True)
class Cell:
    row: int
    col: int


class Board:
    def __init__(self, side=3):
        """
        Creates a game board.

        >>> board = Board(side=3)
        >>> board.side
        3

        >>> board = Board(side=-42)
        Traceback (most recent call last):
        ...
        tictactoe.error.GameValueError: Non-positive board side given
        """
        self.cells = {}

        if side < 1:
            raise GameValueError("Non-positive board side given")
        self.side = side

    def validate(self, cell: Cell):
        """
        Validate cell against board boundaries and availability.

        >>> board = Board(side=3)
        >>> board.validate(Cell(4, 4))
        Traceback (most recent call last):
        ...
        tictactoe.error.GameValueError: Cell is out of bounds
        >>> cell = Cell(0, 1)
        >>> board.move(cell, Player("player"))
        >>> board.validate(cell)
        Traceback (most recent call last):
        ...
        tictactoe.error.GameError: Cell is unavailable
        >>> board.validate(Cell(0, 0)) # should be OK
        """
        if cell.row not in range(self.side) or cell.col not in range(self.side):
            raise GameValueError("Cell is out of bounds")

        if cell in self.cells:
            raise GameError("Cell is unavailable")

    def move(self, cell: Cell, player: Player):
        """
        Attempt to move for specific cell and player.

        >>> board = Board(side=2)
        >>> board.move(Cell(1, 1), Player("player"))
        """
        self.cells[cell] = player

    def is_owner(self, player: Player, cell: Cell):
        return cell in self.cells and self.cells[cell] == player

    def is_winning(self, cell: Cell):
        """
        Check if there is a winning combination containing given cell.

        >>> board = Board(side=2)
        >>> player = Player("player")
        >>> board.move(Cell(0, 0), player)
        >>> board.move(Cell(0, 1), player)
        >>> board.is_winning(Cell(0, 1)) and board.is_winning(Cell(0, 0))
        True
        >>> board.is_winning(Cell(1, 1))
        False
        """
        if cell not in self.cells:
            return False

        player = self.cells[cell]
        return (
            all(self.is_owner(player, Cell(row, cell.col)) for row in range(self.side))
            or all(
                self.is_owner(player, Cell(cell.row, col)) for col in range(self.side)
            )
            or all(
                self.is_owner(player, Cell(rowcol, rowcol))
                for rowcol in range(self.side)
            )
            or all(
                self.is_owner(player, Cell(rowcol, self.side - 1 - rowcol)) == player
                for rowcol in range(self.side)
            )
        )

    @property
    def size(self):
        """
        Return total amount of cells on board.

        >>> board = Board(side=2)
        >>> board.size
        4
        """
        return self.side * self.side

    @property
    def has_available_cells(self):
        """
        Check if there are any available cells.

        >>> board = Board(1)
        >>> board.has_available_cells
        True
        >>> board.move(Cell(0, 0), Player("player"))
        >>> board.has_available_cells
        False
        """
        return len(self.cells) < self.size
