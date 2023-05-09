import socket
from enum import Enum


class Connection:
    def __init__(self, socket):
        self.socket = socket


def connect_to_jvm() -> Connection:
    """Connect to a JVM."""
    sck = socket.socket()
    sck.connect(("localhost", 5005))
    sck.send("JDWP-Handshake".encode("utf-8"))
    shake = sck.recv(1024).decode("ascii")
    if shake != "JDWP-Handshake":
        raise Exception("Handshake failed.")
    header = deserialize_header(sck.recv(11))
    print(header)
    return Connection(sck)


class PackageType(Enum):
    COMMAND = 0x00
    REPLY = 0x80


class CommandSet(Enum):
    EVENT = 64


_command_sets = {64: CommandSet.EVENT}


class Command(Enum):
    COMPOSITE = (CommandSet.EVENT, 100)


_commands = {(CommandSet.EVENT, 100): Command.COMPOSITE}


class Header:
    length: int
    id: int

    def __init__(self, length: int, id: int) -> None:
        self.length = length
        self.id = id


class ReplyHeader(Header):
    code: int

    def __init__(self, length: int, id: int, code: int) -> None:
        super().__init__(length, id)
        self.code = code

    def __repr__(self):
        return f"ReplyHeader(length={self.length}, id={self.id}, code={self.code})"


class CommandHeader(Header):
    cmd_set: CommandSet
    cmd: Command

    def __init__(self, length: int, id: int, cmd_set: int, cmd: int) -> None:
        super().__init__(length, id)
        self.cmd_set = _command_sets[cmd_set]
        self.cmd = _commands[(self.cmd_set, cmd)]

    def __repr__(self):
        return f"CommandHeader(length={self.length}, id={self.id}, cmd_set={self.cmd_set}, cmd={self.cmd})"


def deserialize_header(data: bytes) -> Header:
    """Deserialize a header from a byte string."""
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
