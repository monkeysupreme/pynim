from typing import Optional

from pynim.account import Account
from pynim.datatypes import Transaction
from pynim.hashes import keccak256
from pynim.params import NIM
from pynim.vm.machine import Machine, push_address
from pynim.vm.opcode import OP_STOP


def nim_to_wei(amount_nim: float) -> int:
    return int(amount_nim * NIM)


def wei_to_nim(amount_wei: int) -> float:
    return amount_wei / NIM


def create_coinbase_transaction(
    current_time: int,
    sender: Account,
    recipient: bytes,
    value: int,
    input_data: Optional[bytes],
    vm: Machine,
) -> Transaction:
    bytecode = (
        push_address(sender.address)
        + push_address(recipient)
        + vm.push_u256(value)
        + [OP_STOP]
    )

    vm.load(bytes(bytecode), gas=10)

    coinbase = Transaction(
        timestamp=current_time,
        hash=None,
        nonce=0,
        recipient=b"\x00" * 20,
        sender=sender.address,
        value=value,
        input_data=input_data,
        signature=None,
        gas=0,
        gas_price=0,
    )
    coinbase.hash = keccak256(coinbase.serialize())
    return coinbase
