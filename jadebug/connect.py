import socket


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
    return Connection(sck)
