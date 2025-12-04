import time
from typing import Optional

from pynim.datatypes import Transaction
from pynim.hashes import keccak256

MAX_POOL_SIZE = 10_000
TTL_SECONDS = 3_600
MAX_PER_ACCOUNT = 1_000


class TransactionPoolError(Exception):
    """Base exception for transaction pool errors"""

    pass


class InvalidTransactionError(TransactionPoolError):
    """Raised when a transaction is invalid"""

    pass


class TransactionExistsError(TransactionPoolError):
    """Raised when a transaction already exists in the pool"""

    pass


class TransactionPool:
    def __init__(self) -> None:
        self.transactions: dict[bytes, Transaction] = {}
        self.transactions_by_sender: dict[bytes, list[Transaction]]
        self.transaction_hashes: set[bytes] = set()
        self.transaction_timestamps: dict[bytes, float] = {}

    def add(self, transaction: Transaction, validate: bool = True) -> bool:
        if validate:
            self._validate_transaction(transaction)

        h = transaction.hash or keccak256(transaction.serialize())
        if h in self.transaction_hashes:
            raise TransactionExistsError(f"Transaction {h.hex()} already in pool")

        if len(self.transactions) >= MAX_POOL_SIZE:
            self._cleanup_stale_transactions()

            if len(self.transactions) >= MAX_POOL_SIZE:
                raise TransactionPoolError("Transaction pool is full")

            sender_transactions = self.transactions_by_sender.get(
                transaction.sender, []
            )
            if len(sender_transactions) >= MAX_PER_ACCOUNT:
                raise TransactionPoolError(
                    f"Account {transaction.sender.hex()} has reached transaction limit"
                )

        existing_transaction = self._find_transaction_by_nonce(
            transaction.sender, transaction.nonce
        )
        if existing_transaction:
            if transaction.value <= existing_transaction.value:
                raise InvalidTransactionError(
                    f"Transaction with nonce {transaction.nonce} exists with higher equal value"
                )
            self._remove_transaction(existing_transaction)

        self.transactions[h] = transaction
        self.transaction_hashes.add(h)
        self.transaction_timestamps[h] = time.time()

        self.transactions_by_sender[transaction.sender].append(transaction)
        self.transactions_by_sender[transaction.sender].sort(key=lambda t: t.nonce)

        return True

    def remove(self, hash: bytes) -> bool:
        if hash not in self.transaction_hashes:
            return False

        transaction = self.transactions[hash]
        self._remove_transaction(transaction)
        return True

    def get(self, hash: bytes) -> Optional[Transaction]:
        return self.transactions.get(hash)

    def get_transactions_by_sender(
        self,
        limit: Optional[int] = None,
        account_nonces: Optional[dict[bytes, int]] = None,
    ) -> list[Transaction]:
        pending = []

        for sender, transactions in self.transactions_by_sender.items():
            if not transactions:
                continue

            if account_nonces is not None:
                expected_nonce = account_nonces.get(sender, 0)
                for transaction in transactions:
                    if transaction.nonce == expected_nonce:
                        pending.append(transaction)
                        expected_nonce += 1
                    elif transaction.nonce > expected_nonce:
                        break
            else:
                pending.extend(transactions)

        pending.sort(key=lambda t: t.value, reverse=True)
        if limit:
            return pending[:limit]
        return pending

    def get_all(self) -> list[Transaction]:
        return list(self.transactions.values())

    def contains(self, hash: bytes) -> bool:
        return hash in self.transaction_hashes

    def size(self) -> int:
        return len(self.transactions)

    def clear(self) -> None:
        self.transactions.clear()
        self.transactions_by_sender.clear()
        self.transaction_hashes.clear()
        self.transaction_timestamps.clear()

    def _find_transaction_by_nonce(
        self, sender: bytes, nonce: int
    ) -> Optional[Transaction]:
        sender_transactions = self.transactions_by_sender.get(sender, [])
        for transaction in sender_transactions:
            if transaction.nonce == nonce:
                return transaction

        return None

    def _cleanup_stale_transactions(self) -> int:
        current_time = time.time()
        stale_transactions = []

        for h, timestamp in self.transaction_timestamps.items():
            if current_time - timestamp > TTL_SECONDS:
                stale_transactions.append(h)

            for h in stale_transactions:
                transaction = self.transactions.get(h)
                if transaction:
                    self._remove_transaction(transaction)

        return len(stale_transactions)

    def _remove_transaction(self, transaction: Transaction) -> None:
        h = transaction.hash or keccak256(transaction.serialize())
        if h in self.transactions:
            del self.transactions[h]

        self.transaction_hashes.discard(h)

        if h in self.transaction_timestamps:
            del self.transaction_timestamps[h]

        if transaction.sender in self.transactions_by_sender:
            self.transactions_by_sender[transaction.sender] = [
                t
                for t in self.transactions_by_sender[transaction.sender]
                if (t.hash or keccak256(t.serialize()))
            ]

            if not self.transactions_by_sender[transaction.sender]:
                del self.transactions_by_sender[transaction.sender]

    def _validate_transaction(self, transaction: Transaction) -> None:
        if transaction.sender is None or len(transaction.sender) == 0:
            raise InvalidTransactionError("Transaction missing sender")

        if transaction.recipient is None or len(transaction.recipient) == 0:
            raise InvalidTransactionError("Transaction missing recipient")

        if transaction.value < 0:
            raise InvalidTransactionError("Transaction value cannot be negative")

        if transaction.nonce < 0:
            raise InvalidTransactionError("Transaction nonce cannot be negative")

        current_time = int(time.time())
        if transaction.timestamp > current_time + 300:  # 5 minutes in future
            raise InvalidTransactionError("Transaction timestamp too far in future")

    def get_nonce_gap(self, sender: bytes) -> Optional[int]:
        transactions = self.transactions_by_sender[sender]
        if not transactions:
            return None

        expected_nonce = transactions[0].nonce
        for transaction in transactions:
            if transaction.nonce != expected_nonce:
                return expected_nonce
            expected_nonce += 1

        return None

    def __len__(self) -> int:
        return self.size()

    def __contains__(self, hash: bytes) -> bool:
        return self.contains(hash)
