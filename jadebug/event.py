from __future__ import annotations
from .field import ByteField, IntField, ThreadId
from enum import Enum


class Event:
    kind: EventKind

    def __init__(self, kind: EventKind) -> None:
        self.kind = kind

    @staticmethod
    def deserialize(data: bytes) -> Event:
        event_kind = ByteField.deserialize(data[0:1])
        event = _event_kinds[event_kind.value]
        return event.deserialize(data[1:])


class EventVmStart(Event):
    request_id: IntField
    thread: ThreadId

    def __init__(self, request_id: IntField, thread: ThreadId) -> None:
        super().__init__(EventKind.VM_START)
        self.request_id = request_id
        self.thread = thread

    @staticmethod
    def deserialize(data: bytes) -> EventVmStart:
        request_id = IntField.deserialize(data[0:4])
        thread = ThreadId.deserialize(data[4:])
        return EventVmStart(request_id, thread)

    def __repr__(self):
        return f"EventVmStart(request_id={self.request_id}, thread={self.thread})"


class EventVmDeath(Event):
    request_id: IntField

    def __init__(self, request_id: IntField) -> None:
        super().__init__(EventKind.VM_DEATH)
        self.request_id = request_id

    @staticmethod
    def deserialize(data: bytes) -> EventVmDeath:
        request_id = IntField.deserialize(data[0:4])
        return EventVmDeath(request_id)

    def __repr__(self):
        return f"EventVmDeath(request_id={self.request_id})"


class EventKind(Enum):
    SINGLE_STEP = 1
    BREAKPOINT = 2
    FRAME_POP = 3
    EXCEPTION = 4
    USER_DEFINED = 5
    THREAD_START = 6
    THREAD_DEATH = 7
    THREAD_END = 7
    CLASS_PREPARE = 8
    CLASS_UNLOAD = 9
    CLASS_LOAD = 10
    FIELD_ACCESS = 20
    FIELD_MODIFICATION = 21
    EXCEPTION_CATCH = 30
    METHOD_ENTRY = 40
    METHOD_EXIT = 41
    METHOD_EXIT_WITH_RETURN_VALUE = 42
    MONITOR_CONTENDED_ENTER = 43
    MONITOR_CONTENDED_ENTERED = 44
    MONITOR_WAIT = 45
    MONITOR_WAITED = 46
    VM_START = 90
    VM_INIT = 90
    VM_DEATH = 99
    VM_DISCONNECTED = 100


_event_kinds = {
    EventKind.VM_START.value: EventVmStart,
    EventKind.VM_DEATH.value: EventVmDeath,
}
