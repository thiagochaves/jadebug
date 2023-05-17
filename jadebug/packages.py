from __future__ import annotations
from .field import ByteField, IntField
from .event import Event
from .header import Command, CommandHeader, CommandSet, CommandId, CommandType

_id = 0


def generate_id() -> int:
    global _id
    _id += 1
    return _id


class CommandFactoryImplementation:
    def __init__(self) -> None:
        self._commands: dict[CommandId, type[Command]] = {}
        self.register_command(CommandId(CommandSet.EVENT, 100), CompositeCommand)

    def __call__(self, header: CommandHeader, data: bytes) -> Command:
        return self._commands[header.command_id].deserialize(header, data)

    def register_command(self, command_id: CommandId, cls: type[Command]):
        self._commands[command_id] = cls


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
        return (
            f"CompositeCommand(header={self.header}, "
            f"suspend_policy={self.suspend_policy}, "
            f"event_count={self.event_count}, "
            f"events={self.events})"
        )


class ResumeCommand(Command):
    header: CommandHeader

    def __init__(self) -> None:
        self.header = CommandHeader.from_command_id(11, generate_id(), CommandType.RESUME.value)

    def serialize(self) -> bytes:
        return self.header.serialize()
