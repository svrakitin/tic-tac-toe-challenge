import pytest

from tictactoe.event.store import Eventstore


@pytest.fixture
def eventstore():
    return Eventstore()


def test_stream_holds_events(eventstore):
    eventstore.sink("test", [1, 2, 3])
    eventstore.sink("test", [4, 5, 6])

    assert "test" in eventstore

    assert list(eventstore.stream("test")) == [1, 2, 3, 4, 5, 6]


def test_consumer_can_attach_to_stream(eventstore):
    consumed = []

    def consume(event, id):
        consumed.append(event)

    eventstore.attach(consume)
    eventstore.sink("test", [1, 2, 3])

    assert consumed == [1, 2, 3]
