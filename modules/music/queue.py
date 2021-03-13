from random import shuffle

class Queue:

    def __init__(self):
        self.queue = []

    def add_song(self, song: str):
        self.queue.append(song)

    def remove_song(self, song: int):
        self.queue.remove(song-1)

    def get_song(self, song: int) -> str:
        return self.queue[song-1]

    def get_queue(self) -> list:
        return self.queue

    def clear(self):
        self.queue.clear()

    def shuffle(self):
        shuffle(self.queue)
