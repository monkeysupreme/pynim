import json
from pathlib import Path
from typing import Optional

from pynim.hashes import keccak256

from Crypto.PublicKey import DSA


ADDRESS_LENGTH = 20


class Account:
    """
    Account

    - A Nim Account holds / stores a public and private key
    - Once an account has been created, it can be used to deploy
      smart contracts and send / receive NIM
    - You can NOT delete an account once created

    Params
        code: Bytecode for a Nim Smart Contract

        key_storage: Stores your keys in memory

        balance: Your balance in NIM

        nonce: A transaction counter. This is also
        used for security, as no two transactions
        can have the same nonce

        public_key: A cryptographic key that gives you access
        to your funds and allows other people to
        send NIM
    """

    def __init__(
            self,
            code: Optional[bytes],
            key_storage: dict[bytes, bytes],
            balance: float = 0.0,
            nonce: int = 0,
            public_key: Optional[bytes] = None,
    ) -> None:
        self.code = code
        self.key_storage = key_storage
        self.balance = balance
        self.nonce = nonce
        self.public_key = public_key

    @property
    def address(self) -> bytes:
        if not self.public_key:
            raise ValueError("public key is null")
        return keccak256(self.public_key)[:ADDRESS_LENGTH]

    @classmethod
    def load(cls, path: str) -> "Account":
        path = Path(path) # type: ignore
        with path.open("r") as f: # type: ignore
            j = json.load(f)

        code = bytes.fromhex(j["code"]) if isinstance(j["code"], str) else j["code"]
        public_key = bytes.fromhex(j["public_key"]) if isinstance(j["public_key"], str) else j["public_key"]

        key_storage = dict(j["key_storage"])
        balance = int(j["balance"])
        nonce = int(j["nonce"])

        return cls(code, key_storage, balance, nonce, public_key)

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump({
                "code": self.code,
                "key_storage": {k.hex(): v.hex() for k, v in self.key_storage.items()},
                "balance": self.balance,
                "nonce": self.nonce,
                "public_key": self.public_key.hex() if self.public_key else b"\x00".hex() * 32,
            }, f, indent=4)

    def generate_keys(self) -> None:
        private_key = DSA.generate(2048)
        private_key_bytes = private_key.exportKey()
        public_key_bytes = private_key.public_key().exportKey()
        self.public_key = public_key_bytes
        self.key_storage[public_key_bytes] = private_key_bytes

    def get_key(self, public_key_bytes: bytes) -> bytes:
        return self.key_storage[public_key_bytes]

    def to_json(self, indent: Optional[int] = None) -> str:
        # TODO: add 'address' to the JSON data
        return json.dumps({
            "code": self.code.hex() if self.code else b"\x00".hex() * 10,
            "key_storage": {k: v for k, v in self.key_storage.items()},
            "balance": self.balance,
            "nonce": self.nonce,
            "public_key": self.public_key.hex() if self.public_key else b"\x00".hex() * 32,
        }, indent=indent)