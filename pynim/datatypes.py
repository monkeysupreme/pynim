from typing import Optional

from pynim.hashes import keccak256
from pynim.serialization import Serializable


class Transaction(Serializable):
    def __init__(
        self,
        timestamp: int,
        hash: Optional[bytes],
        nonce: int,
        recipient: bytes,
        sender: bytes,
        value: int,
        input_data: Optional[bytes],
        signature: Optional[bytes],
        gas: int,
        gas_price: int,
    ) -> None:
        self.timestamp = timestamp
        self.hash = hash
        self.nonce = nonce
        self.recipient = recipient
        self.sender = sender
        self.value = value
        self.input_data = input_data
        self.signature = signature
        self.gas = gas
        self.gas_price = gas_price

    def calculate_gas_in_nim(self) -> int:
        return self.gas * self.gas_price

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "hash": self.hash.hex() if self.hash else b"\x00" * 32,
            "nonce": self.nonce,
            "recipient": self.recipient.hex(),
            "sender": self.sender.hex(),
            "value": self.value,
            "input_data": self.input_data.hex() if self.input_data else b"\x00" * 10,
            "signature": self.signature.hex() if self.signature else b"\x00" * 64,
        }


class Header(Serializable):
    def __init__(
        self,
        timestamp: int,
        parent_hash: bytes,
        number: int,
        gas_limit: int,
        gas_used: int,
        base_fee: int,
    ) -> None:
        self.timestamp = timestamp
        self.parent_hash = parent_hash
        self.number = number
        self.gas_limit = gas_limit
        self.gas_used = gas_used
        self.base_fee = base_fee

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "parent_hash": self.parent_hash.hex(),
            "number": self.number,
            "gas_limit": self.gas_limit,
            "gas_used": self.gas_used,
            "base_fee": self.base_fee,
        }


class Block(Serializable):
    def __init__(
        self,
        header: Header,
        transactions: list[Transaction],
        cached_hash: Optional[bytes],
    ) -> None:
        self.header = header
        self.transactions = transactions
        self.cached_hash = cached_hash

    def hash(self) -> bytes:
        return keccak256(self.header.serialize())

    def to_dict(self) -> dict:
        return {
            "header": self.header.to_dict(),
            "transactions": [
                t.hash.hex() if t.hash else b"\x00".hex() * 32
                for t in self.transactions
            ],
            "cached_hash": self.cached_hash.hex() if self.cached_hash else b"\x00" * 32,
        }
