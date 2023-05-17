from __future__ import annotations
from typing import Protocol, Type
import socket
from enum import Enum
from dataclasses import dataclass


_header_length = 11


class PackageType(Enum):
    COMMAND = 0x00
    REPLY = 0x80


class CommandSet(Enum):
    EVENT = 64
    VIRTUAL_MACHINE = 1


_command_sets = {
    64: CommandSet.EVENT,
    1: CommandSet.VIRTUAL_MACHINE,
}


@dataclass(frozen=True)
class CommandId:
    command_set: CommandSet
    command_code: int


class CommandType(Enum):
    COMPOSITE_EVENT = CommandId(CommandSet.EVENT, 100)
    RESUME = CommandId(CommandSet.VIRTUAL_MACHINE, 9)


class Command:
    @staticmethod
    def deserialize(header: CommandHeader, data: bytes) -> Command:
        return Command()

    def serialize(self) -> bytes:
        return b""


class Reply:
    header: ReplyHeader

    def __init__(self, header: ReplyHeader) -> None:
        self.header = header

    def __repr__(self):
        return f"Reply(header={self.header})"


class Header:
    length: int
    id: int

    def __init__(self, length: int, id: int) -> None:
        self.length = length
        self.id = id

    def deserialize(
        self, socket: socket.socket, factory: CommandFactory
    ) -> Reply | Command:
        return Command()

    def serialize(self) -> bytes:
        return b""


class ReplyHeader(Header):
    code: int

    def __init__(self, length: int, id: int, code: int) -> None:
        super().__init__(length, id)
        self.code = code

    def __repr__(self):
        return f"ReplyHeader(length={self.length}, id={self.id}, code={self.code})"

    def deserialize(self, socket: socket.socket, factory: CommandFactory) -> Reply:
        return Reply(self)


class CommandHeader(Header):
    command_id: CommandId

    def __init__(self, length: int, id: int, cmd_set: int, cmd: int) -> None:
        super().__init__(length, id)
        self.command_id = CommandId(_command_sets[cmd_set], cmd)

    @classmethod
    def from_command_id(cls, length: int, id: int, command_id: CommandId) -> CommandHeader:
        return cls(length, id, command_id.command_set.value, command_id.command_code)

    def __repr__(self):
        return (
            f"CommandHeader(length={self.length}, "
            f"id={self.id}, "
            f"cmd_id={self.command_id})"
        )

    def deserialize(self, socket: socket.socket, factory: CommandFactory) -> Command:
        data = socket.recv(self.length - _header_length)
        return factory(self, data)

    def serialize(self) -> bytes:
        return (
            self.length.to_bytes(4, byteorder="big")
            + self.id.to_bytes(4, byteorder="big")
            + PackageType.COMMAND.value.to_bytes(1, byteorder="big")
            + self.command_id.command_set.value.to_bytes(1, byteorder="big")
            + self.command_id.command_code.to_bytes(1, byteorder="big")
        )


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


class CommandFactory(Protocol):
    def __call__(self, header: CommandHeader, data: bytes) -> Command:
        ...

    def register_command(self, cmd_set: CommandSet, cmd: int, cls: Type[Command]):
        ...
