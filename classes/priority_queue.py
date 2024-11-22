import heapq
from dataclasses import dataclass, field
from typing import Any

class PriorityQueue:
    def __init__(self):
        self.q = []

    def push(self, priority, item):
        heapq.heappush(self.q, PriorityQueueItem(-priority, item))

    # Returns highest priority item in the queue
    def pop(self):
        item = heapq.heappop(self.q)
        return (item.priority, item.item)

    def __len__(self):
        return len(self.q)

@dataclass(order=True)
class PriorityQueueItem:
    priority: int
    item: Any = field(compare=False)