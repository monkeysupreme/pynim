from pynim.account import Account
from pynim.consensus import ConsensusEngine
from pynim.database import Database
from pynim.datatypes import Block, Header, Transaction
from pynim.genesis import GenesisBlock
from pynim.vm.machine import Machine
from pynim.hashes import keccak256
from pynim.transaction_pool import TransactionPool
import time
from typing import Optional


class Blockchain:
    def __init__(
            self,
            chain_id: str,
            genesis_block: GenesisBlock,
            current_block: Optional[Block],
            block_by_hash: dict[bytes, Block],
            disk: Database,
            accounts: list[Account],
            machine: Machine,
            consensus: ConsensusEngine,
            transaction_pool: Optional[TransactionPool] = None,
    ) -> None:
        self.chain_id = chain_id
        self.genesis_block = genesis_block
        self.current_block = current_block or genesis_block
        self.block_by_hash = block_by_hash
        self.disk = disk
        self.accounts = accounts
        self.machine = machine
        self.consensus = consensus
        self.transaction_pool = transaction_pool or TransactionPool()

    def generate_new_block(self, gas_limit: int = 30_000_000, base_fee: int = 1) -> Block:
        parent_hash = self.current_block.hash() if self.current_block else None
        proposer = self.consensus.select_proposer()

        account_nonces = {acc.address: acc.nonce for acc in self.accounts}
        pending_transactions = self.transaction_pool.get_pending(limit=1000, account_nonces=account_nonces)

        gas_used = sum(transaction.value for transaction in pending_transactions)
        timestamp = int(time.time())
        number = 0 if parent_hash is None else self.current_block.header.number + 1

        header = Header(
            timestamp=timestamp,
            parent_hash=parent_hash if parent_hash else b"\x00"*32,
            number=number,
            gas_limit=gas_limit,
            gas_used=gas_used,
            base_fee=base_fee,
        )

        block_hash = keccak256(header.serialize())
        block = Block(
            header=header,
            transactions=pending_transactions,
            cached_hash=block_hash
        )

        self.block_by_hash[block_hash] = block
        self.current_block = block
        self.consensus.current_head = block_hash

        self.disk.write(block.hash(), block.serialize())

        transaction_hashes = [transaction.hash for transaction in pending_transactions if transaction.hash]
        self.transaction_pool.remove_batch(transaction_hashes)

        return block
    
    def add_block(self, block: Block) -> bool:
        if not self.consensus.verify_block(block):
            return False
        h = block.hash()
        self.block_by_hash[h] = block
        self.current_block = block
        self.consensus.current_head = h
        
        transaction_hashes = [transaction.hash for transaction in block.transactions if transaction.hash]
        self.transaction_pool.remove_batch(transaction_hashes)
        
        return True

    def add_transaction(self, transaction: Transaction) -> bool:
        try:
            return self.transaction_pool.add(transaction)
        except Exception as e:
            return False

    def get_pending_transactions(self, limit: Optional[int] = None) -> list[Transaction]:
        account_nonces = {acc.address: acc.nonce for acc in self.accounts}
        return self.transaction_pool.get_pending(limit=limit, account_nonces=account_nonces)

    def get_transaction(self, transaction_hash: bytes) -> Optional[Transaction]:
        return self.transaction_pool.get(transaction_hash)

    def get_block_by_hash(self, block_hash: bytes) -> Optional[Block]:
        return self.block_by_hash.get(block_hash)

    def get_latest_block(self) -> Block:
        return self.current_block

    def validate_block(self, block: Block) -> bool:
        return self.consensus.verify_block(block)

    def chain_height(self) -> int:
        return self.current_block.header.number if self.current_block else 0