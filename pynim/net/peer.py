import socket

from pynim.serialization import Serializable


class Peer(Serializable):
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    @property
    def address(self) -> tuple[str, int]:
        return self.host, self.port

    def to_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
        }
