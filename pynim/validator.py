from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from pynim.datatypes import Block, Header, Transaction
from pynim.hashes import keccak256



class Status(Enum):
    ACTIVE = auto()
    INACTIVE = auto()
    SLASHED = auto()


@dataclass
class ValidatorStatus:
    status: Status = Status.ACTIVE

    def set_status(self, new_status: Status) -> None:
        self.status = new_status

    @property
    def active(self) -> bool:
        return self.status == Status.ACTIVE

    @property
    def inactive(self) -> bool:
        return self.status == Status.INACTIVE

    @property
    def slashed(self) -> bool:
        return self.status == Status.SLASHED


class Validator:
    def __init__(
            self,
            public_key: bytes,
            stake: int,
            reward_balance: int,
            block_by_hash: dict[bytes, Block],
            status: ValidatorStatus,
    ) -> None:
        self.public_key = public_key
        self.stake = stake
        self.reward_balance = reward_balance
        self.block_by_hash = block_by_hash
        self.status = status

    def build_block(
        self,
        parent_hash: Optional[bytes],
        timestamp: int,
        gas_limit: int,
        base_fee: int,
        transactions: list[Transaction]
    ) -> Block:
        number = 0 if parent_hash is None else self.block_by_hash[parent_hash].header.number + 1
        h = Header(
            timestamp=timestamp,
            parent_hash=parent_hash if parent_hash else b"\x00" * 32,
            number=number,
            gas_limit=gas_limit,
            gas_used=sum(t.value for t in transactions),
            base_fee=base_fee,
        )
        for tx in transactions:
            if tx.hash is None:
                tx.hash = keccak256(tx.serialize())
        blk = Block(
            header=h,
            transactions=transactions,
            cached_hash=keccak256(h.serialize())
        )
        return blk
