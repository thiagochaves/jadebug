from __future__ import annotations
import socket
from .header import (
    Command,
    deserialize_header,
    Reply
)
from .packages import CommandFactoryImplementation


class Connection:
    def __init__(self, socket):
        self.socket = socket
        self.factory = CommandFactoryImplementation()

    def read_package(self) -> Command | Reply:
        header = deserialize_header(self.socket)
        package = header.deserialize(self.socket, self.factory)
        return package


def connect_to_jvm() -> Connection:
    """Connect to a JVM."""
    sck = socket.socket()
    sck.connect(("localhost", 5005))
    handshake_string = "JDWP-Handshake"
    sck.send(handshake_string.encode("utf-8"))
    shake = sck.recv(len(handshake_string)).decode("ascii")
    if shake != handshake_string:
        raise Exception("Handshake failed.")
    return Connection(sck)
