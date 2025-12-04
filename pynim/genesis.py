import json
from pathlib import Path
from pynim.account import Account
from pynim.datatypes import Block, Header, Transaction
from pynim.hashes import keccak256
from pynim.serialization import Serializable
from pynim.utils import create_coinbase_transaction, nim_to_wei
from pynim.vm.machine import Machine


class GenesisBlock(Block, Serializable):
    def __init__(self, current_time: int, account: Account) -> None:
        self.current_time = current_time
        self.account = account
        self.header: Header = Header(
            timestamp=current_time,
            parent_hash=b"\x00" * 32,
            number=1,
            gas_limit=0,
            gas_used=0,
            base_fee=0,
        )

        self.vm = Machine()

        self.transactions: list[Transaction] = [
            create_coinbase_transaction(
                current_time=current_time,
                sender=account,
                recipient=account.address,
                value=nim_to_wei(100),
                input_data=self.vm.code,
                vm=self.vm,
            )
        ]

    def hash(self) -> bytes:
        return keccak256(self.serialize())

    def to_dict(self) -> dict:
        transaction_hashes = [
            t.hash.hex() if t.hash else b"\x00".hex() * 32 for t in self.transactions
        ]
        return {
            "header": self.header.to_dict(),
            "transactions": transaction_hashes,
            "account": self.account.address.hex(),
            "current_time": self.current_time,
            "input_data": self.vm.code.hex(),
        }
    
    @classmethod
    def read(cls, path: str) -> "GenesisBlock":
        with open(Path(path), "r") as f:
            data = json.load(f)

        account = Account.load("account.json")

        genesis = cls(current_time=data["current_time"], account=account)

        if "input_data" in data:
            genesis.vm.code = bytes.fromhex(data["input_data"])

        txs = []
        for tx_hash_hex in data.get("transactions", []):
            tx = Transaction(
                timestamp=data["current_time"],
                hash=bytes.fromhex(tx_hash_hex) if tx_hash_hex else None,
                nonce=0,
                sender=account.address,
                recipient=account.address,
                value=nim_to_wei(100),
                input_data=genesis.vm.code,
                signature=None,
            )
            txs.append(tx)
        genesis.transactions = txs

        return genesis