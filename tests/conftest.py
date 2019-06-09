import pytest
from tictactoe.player import Player


@pytest.fixture
def players():
    return [Player("alice"), Player("bob")]
