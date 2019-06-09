from collections import defaultdict


class Eventstore:
    def __init__(self):
        self.consumers = []
        self.__streams = defaultdict(list)

    def sink(self, stream_id, events):
        self.__streams[stream_id].extend(events)

        for event in events:
            for consumer in self.consumers:
                consumer(event, stream_id)

    def stream(self, stream_id):
        if not stream_id in self.__streams:
            raise KeyError(stream_id)

        yield from self.__streams[stream_id]

    def attach(self, func):
        self.consumers.append(func)

    def __contains__(self, key):
        return self.__streams.__contains__(key)
