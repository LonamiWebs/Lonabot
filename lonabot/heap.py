# The design of heapq is horrible, just go see:
# https://docs.python.org/3/library/heapq.html
import heapq


class Heap:
    """Pythonic heap."""
    def __init__(self, iterable=()):
        self._heap = list(iterable)
        heapq.heapify(self._heap)

    def push(self, item):
        heapq.heappush(self._heap, item)

    def pop(self):
        return heapq.heappop(self._heap)

    def peek(self):
        return self._heap[0]

    def __bool__(self):
        return bool(self._heap)
