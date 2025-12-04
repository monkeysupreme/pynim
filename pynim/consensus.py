from typing import Optional

from pynim.datatypes import Block, Header, Transaction
from pynim.hashes import keccak256


class ConsensusEngine:
    def __init__(
        self,
        block_time: int,
        validator_stakes: dict[bytes, int],
        validators: list[bytes],
        block_by_hash: dict[bytes, Block],
    ) -> None:
        self.block_time = block_time
        self.validator_stakes = validator_stakes
        self.validators = validators
        self.block_by_hash = block_by_hash
        self.current_head: Optional[bytes] = None
        self.slash_penalty = 10

    def select_proposer(self) -> bytes:
        total = sum(max(1, self.validator_stakes.get(v, 0)) for v in self.validators)
        seed = keccak256(
            self.current_head if self.current_head is not None else b"\x00" * 32
        )
        r = int.from_bytes(seed, "big") % total
        cum = 0
        for v in self.validators:
            st = max(1, self.validator_stakes.get(v, 0))
            cum += st
            if r < cum:
                return v
        return self.validators[0]

    def validate_block_header(self, header: Header) -> bool:
        if self.current_head:
            parent = self.block_by_hash.get(self.current_head)
            if not parent:
                return False
            if header.number != parent.header.number + 1:
                return False
            if header.timestamp < parent.header.timestamp + self.block_time:
                return False
        return True

    def validate_transactions(self, txs: list[Transaction]) -> bool:
        seen_nonces = {}
        for tx in txs:
            if tx.sender not in seen_nonces:
                seen_nonces[tx.sender] = tx.nonce
            else:
                if tx.nonce <= seen_nonces[tx.sender]:
                    return False
                seen_nonces[tx.sender] = tx.nonce
        return True

    def verify_block(self, block: Block) -> bool:
        if not self.validate_block_header(block.header):
            return False
        if not self.validate_transactions(block.transactions):
            return False
        return True

    def apply_block(self, block: Block) -> bool:
        if not self.verify_block(block):
            self.slash(self.select_proposer())
            return False
        h = block.hash()
        self.block_by_hash[h] = block
        self.current_head = h
        return True

    def finalize_block(self) -> Optional[bytes]:
        return self.current_head

    def slash(self, validator: bytes) -> None:
        stake = self.validator_stakes.get(validator, 0)
        new_stake = max(0, stake - self.slash_penalty)
        self.validator_stakes[validator] = new_stake
        if new_stake == 0 and validator in self.validators:
            self.validators.remove(validator)
