from __future__ import annotations
import socket
from enum import Enum
import typing


_header_length = 11


class Connection:
    def __init__(self, socket):
        self.socket = socket


def connect_to_jvm() -> Connection:
    """Connect to a JVM."""
    sck = socket.socket()
    sck.connect(("localhost", 5005))
    handshake_string = "JDWP-Handshake"
    sck.send(handshake_string.encode("utf-8"))
    shake = sck.recv(len(handshake_string)).decode("ascii")
    if shake != handshake_string:
        raise Exception("Handshake failed.")
    header = deserialize_header(sck)
    package = header.deserialize(sck)
    print(package)
    return Connection(sck)


class PackageType(Enum):
    COMMAND = 0x00
    REPLY = 0x80


class CommandSet(Enum):
    EVENT = 64


_command_sets = {64: CommandSet.EVENT}


class Command:
    @staticmethod
    def deserialize(header: CommandHeader, data: bytes) -> Command:
        return Command()


class Reply:
    pass


class CompositeCommand(Command):
    header: CommandHeader
    suspend_policy: ByteField
    event_count: IntField
    events: list[Event]

    def __init__(
        self,
        header: CommandHeader,
        suspend_policy: ByteField,
        event_count: IntField,
        events: list[Event],
    ) -> None:
        self.header = header
        self.suspend_policy = suspend_policy
        self.event_count = event_count
        self.events = events

    @staticmethod
    def deserialize(header: CommandHeader, data: bytes) -> CompositeCommand:
        suspend_policy = ByteField.deserialize(data[0:1])
        event_count = IntField.deserialize(data[1:5])
        events = []
        for _ in range(event_count.value):
            events.append(Event.deserialize(data[5:]))
        return CompositeCommand(header, suspend_policy, event_count, events)

    def __repr__(self):
        return f"CompositeCommand(header={self.header}, suspend_policy={self.suspend_policy}, event_count={self.event_count}, events={self.events})"


_commands = {(CommandSet.EVENT, 100): CompositeCommand}


class ByteField:
    value: int

    def __init__(self, value: int) -> None:
        self.value = value

    @staticmethod
    def deserialize(data: bytes) -> ByteField:
        return ByteField(int.from_bytes(data[0:1], byteorder="big"))

    def __repr__(self):
        return f"ByteField(value={self.value})"


class IntField:
    value: int

    def __init__(self, value: int) -> None:
        self.value = value

    @staticmethod
    def deserialize(data: bytes) -> IntField:
        return IntField(int.from_bytes(data[0:4], byteorder="big"))

    def __repr__(self):
        return f"IntField(value={self.value})"


class Event:
    @staticmethod
    def deserialize(data: bytes) -> Event:
        event_kind = ByteField.deserialize(data[0:1])
        event = _event_kinds[event_kind.value]
        return event.deserialize(data[1:])


class EventVmStart(Event):
    request_id: IntField
    thread: ThreadId

    def __init__(self, request_id: IntField, thread: ThreadId) -> None:
        self.request_id = request_id
        self.thread = thread

    @staticmethod
    def deserialize(data: bytes) -> EventVmStart:
        request_id = IntField.deserialize(data[0:4])
        thread = ThreadId.deserialize(data[4:])
        return EventVmStart(request_id, thread)

    def __repr__(self):
        return f"EventVmStart(request_id={self.request_id}, thread={self.thread})"


class ThreadId:
    value: int

    def __init__(self, value: int) -> None:
        self.value = value

    @staticmethod
    def deserialize(data: bytes) -> ThreadId:
        return ThreadId(int.from_bytes(data[0:8], byteorder="big"))

    def __repr__(self):
        return f"ThreadId(value={self.value})"


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


_event_kinds = {EventKind.VM_START.value: EventVmStart}


class Header:
    length: int
    id: int

    def __init__(self, length: int, id: int) -> None:
        self.length = length
        self.id = id

    def deserialize(self, socket: socket.socket) -> typing.Union[Reply, Command]:
        return Command()


class ReplyHeader(Header):
    code: int

    def __init__(self, length: int, id: int, code: int) -> None:
        super().__init__(length, id)
        self.code = code

    def __repr__(self):
        return f"ReplyHeader(length={self.length}, id={self.id}, code={self.code})"

    def deserialize(self, socket: socket.socket) -> Reply:
        return Reply()


class CommandHeader(Header):
    cmd_set: CommandSet
    cmd: typing.Type[Command]

    def __init__(self, length: int, id: int, cmd_set: int, cmd: int) -> None:
        super().__init__(length, id)
        self.cmd_set = _command_sets[cmd_set]
        self.cmd = _commands[(self.cmd_set, cmd)]

    def __repr__(self):
        return f"CommandHeader(length={self.length}, id={self.id}, cmd_set={self.cmd_set}, cmd={self.cmd})"

    def deserialize(self, socket: socket.socket) -> Command:
        data = socket.recv(self.length - _header_length)
        return self.cmd.deserialize(self, data)


def deserialize_header(socket: socket.socket) -> Header:
    """Deserialize a header from a connected socket."""
    data = socket.recv(_header_length)
    length = int.from_bytes(data[0:4], byteorder="big")
    id = int.from_bytes(data[4:8], byteorder="big")
    flags = int.from_bytes(data[8:9], byteorder="big")
    code = int.from_bytes(data[9:11], byteorder="big")
    cmd_set = int.from_bytes(data[9:10], byteorder="big")
    cmd = int.from_bytes(data[10:11], byteorder="big")
    if flags == PackageType.COMMAND.value:
        return CommandHeader(length, id, cmd_set, cmd)
    elif flags == PackageType.REPLY.value:
        return ReplyHeader(length, id, code)
    else:
        raise Exception(f"Unknown flags: {flags}")
