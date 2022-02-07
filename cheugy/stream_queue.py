
class StreamQueue:

    repeat = False
    current = None
    streams = []

    def next(self):

        if self.repeat and self.current is not None:
            return self.current

        self.current = None

        if len(self.streams) > 0:
            self.current = self.streams.pop(0)

        return self.current

    def add(self, url):
        self.streams.append(url)

    def clear(self):
        self.current = None
        self.streams.clear()

    def __len__(self):
        return len(self.streams)
