from __future__ import annotations


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


class ThreadId:
    value: int

    def __init__(self, value: int) -> None:
        self.value = value

    @staticmethod
    def deserialize(data: bytes) -> ThreadId:
        return ThreadId(int.from_bytes(data[0:8], byteorder="big"))

    def __repr__(self):
        return f"ThreadId(value={self.value})"
