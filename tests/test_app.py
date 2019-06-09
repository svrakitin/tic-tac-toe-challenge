import pytest
from falcon import testing

from tictactoe.api import create_api


@pytest.fixture
def client():
    return testing.TestClient(create_api())


def test_no_games(client: testing.TestClient):
    result = client.simulate_get("/api/games")
    assert result.json == {}
    assert result.status_code == 200


def test_attempt_to_get_non_existent_game(client: testing.TestClient):
    result = client.simulate_get("/api/games/notexists")
    assert result.status_code == 404


def test_attempt_to_post_non_existent_game(client: testing.TestClient):
    result = client.simulate_post("/api/games/notexists", json={"player": "alice"})
    assert result.status_code == 404


def test_should_create_game(client: testing.TestClient):
    result = client.simulate_post("/api/games")

    assert result.status_code == 201

    game_id = result.json["id"]

    result = client.simulate_get(f"/api/games/{game_id}")

    assert result.status_code == 200
    assert result.json == {
        "state": "PENDING",
        "board": [[None, None, None], [None, None, None], [None, None, None]],
        "players": [],
        "winner": None,
    }


def test_list_games(client: testing.TestClient):
    result = client.simulate_post("/api/games", json={"board_side": 1})

    game_id = result.json["id"]

    result: testing.Result = client.simulate_get("/api/games")

    assert result.json == {
        game_id: {"state": "PENDING", "board": [[None]], "players": [], "winner": None}
    }


def test_should_join_two_players(client: testing.TestClient):
    result = client.simulate_post("/api/games")

    game_id = result.json["id"]
    game_path = f"/api/games/{game_id}"

    join_alice = client.simulate_post(game_path, json={"player": "alice"})

    assert join_alice.status_code == 202

    join_bob = client.simulate_post(game_path, json={"player": "bob"})

    assert join_bob.status_code == 202

    result = client.simulate_get(game_path)

    assert result.status_code == 200
    assert result.json == {
        "state": "PLAYABLE",
        "board": [[None, None, None], [None, None, None], [None, None, None]],
        "players": ["alice", "bob"],
        "winner": None,
    }


def test_player_should_win(client: testing.TestClient):
    result = client.simulate_post("/api/games", json={"board_side": 2})

    game_id = result.json["id"]
    game_path = f"/api/games/{game_id}"

    client.simulate_post(game_path, json={"player": "alice"})
    client.simulate_post(game_path, json={"player": "bob"})

    client.simulate_post(
        game_path, json={"player": "alice", "cell": {"row": 0, "col": 0}}
    )
    client.simulate_post(
        game_path, json={"player": "bob", "cell": {"row": 0, "col": 1}}
    )
    client.simulate_post(
        game_path, json={"player": "alice", "cell": {"row": 1, "col": 0}}
    )

    result = client.simulate_get(game_path)
    assert result.json == {
        "state": "FINISHED",
        "board": [[0, 1], [0, None]],
        "players": ["alice", "bob"],
        "winner": "alice",
    }


def test_attempt_to_move_twice(client: testing.TestClient):
    result = client.simulate_post("/api/games", json={"board_side": 2})

    game_id = result.json["id"]
    game_path = f"/api/games/{game_id}"

    client.simulate_post(game_path, json={"player": "alice"})
    client.simulate_post(game_path, json={"player": "bob"})

    client.simulate_post(
        game_path, json={"player": "alice", "cell": {"row": 0, "col": 0}}
    )

    result = client.simulate_post(
        game_path, json={"player": "alice", "cell": {"row": 0, "col": 1}}
    )

    assert result.status_code == 500
    assert result.json == {"title": "Player already moved"}


def test_attempt_to_move_being_the_single_player(client: testing.TestClient):
    result = client.simulate_post("/api/games", json={"board_side": 2})

    game_id = result.json["id"]
    game_path = f"/api/games/{game_id}"

    client.simulate_post(game_path, json={"player": "alice"})

    result = client.simulate_post(
        game_path, json={"player": "alice", "cell": {"row": 0, "col": 0}}
    )

    assert result.status_code == 500
    assert result.json == {"title": "Game is not PLAYABLE"}
