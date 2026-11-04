"""Event bus for reactive decoupled UI updates in LifeOS.
"""

from collections import defaultdict
from typing import Callable, Any

class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable[..., Any]):
        if callback not in self._subscribers[event_name]:
            self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable[..., Any]):
        if callback in self._subscribers[event_name]:
            self._subscribers[event_name].remove(callback)

    def emit(self, event_name: str, *args, **kwargs):
        for callback in list(self._subscribers[event_name]):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"[EventBus Error] in {event_name}: {e}")

bus = EventBus()
