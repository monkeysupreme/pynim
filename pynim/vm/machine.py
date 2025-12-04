from pynim.datatypes import Transaction
from pynim.vm.opcode import (
    OP_ADD,
    OP_ADDRESS,
    OP_BALANCE,
    OP_BASEFEE,
    OP_BLOCKHASH,
    OP_CODESIZE,
    OP_DIV,
    OP_GASLIMIT,
    OP_GASPRICE,
    OP_LOAD,
    OP_MOD,
    OP_MUL,
    OP_NUMBER,
    OP_PUSH,
    OP_PUSH32,
    OP_SELFBALANCE,
    OP_STOP,
    OP_STORE,
    OP_SUB,
    OP_TIMESTAMP,
)

MAX_STACK = 256


GAS_COST = {
    OP_STOP: 0,
    OP_ADD: 3,
    OP_SUB: 3,
    OP_MUL: 5,
    OP_DIV: 5,
    OP_MOD: 5,
    OP_PUSH: 3,
    OP_PUSH32: 3,
    OP_ADDRESS: 2,
    OP_BALANCE: 20,
    OP_CODESIZE: 2,
    OP_GASPRICE: 1,
    OP_BLOCKHASH: 20,
    OP_TIMESTAMP: 2,
    OP_NUMBER: 2,
    OP_GASLIMIT: 2,
    OP_BASEFEE: 2,
    OP_SELFBALANCE: 5,
    OP_STORE: 20,
    OP_LOAD: 5,
}


class OutOfGas(Exception):
    pass


class StackOverflow(Exception):
    pass


class StackUnderflow(Exception):
    pass


class Machine:
    def __init__(self, address=0, balance=0, gas_price=1, block_env=None) -> None:
        self.pc: int = 0
        self.stack: list[int] = []
        self.memory: bytearray = bytearray()
        self.storage: dict[int, int] = {}
        self.gas: int = 0
        self.stopped: bool = False
        self.code: bytes = bytes()

        self.address = address
        self.balance = balance
        self.gas_price = gas_price

        self.block_env = block_env or {
            "blockhash": 0,
            "timestamp": 0,
            "number": 0,
            "gaslimit": 0,
            "basefee": 0,
        }

    def load(self, code: bytes, gas: int) -> None:
        self.code = code
        self.pc = 0
        self.gas = gas
        self.stopped = False

    def charge_gas(self, opcode: int) -> None:
        cost = GAS_COST.get(opcode, None)
        if cost is None:
            raise Exception(f"gas cost undefined for opcode: {hex(opcode)}")
        if self.gas < cost:
            raise Exception("execution ran out of gas")
        self.gas -= cost

    def _push(self, x: int | str) -> None:
        if len(self.stack) > MAX_STACK:
            raise StackOverflow("Stack overflow")
        self.stack.append(x & ((1 << 256) - 1))  # type: ignore

    def _pop(self) -> int:
        if not self.stack:
            raise StackUnderflow("Stack underflow")
        return self.stack.pop()

    def peek(self, n: int = 0) -> int:
        if n >= len(self.stack):
            raise StackUnderflow("stack underflow on peek")
        return self.stack[-1 - n]

    def step(self) -> None:
        opcode = self.code[self.pc]
        self.pc += 1

        self.charge_gas(opcode)

        if opcode == OP_STOP:
            self.stopped = True
            return

        if opcode == OP_ADD:
            b = self._pop()
            a = self._pop()
            self._push(a + b)
            return

        if opcode == OP_SUB:
            b = self._pop()
            a = self._pop()
            self._push(a - b)
            return

        if opcode == OP_MUL:
            b = self._pop()
            a = self._pop()
            self._push(a * b)
            return

        if opcode == OP_DIV:
            b = self._pop()
            a = self._pop()
            self._push(a // b)
            return

        if opcode == OP_MOD:
            b = self._pop()
            a = self._pop()
            self._push(0 if b == 0 else a % b)
            return

        if opcode == OP_PUSH:
            if self.pc >= len(self.code):
                raise Exception("PUSH missing immediate value")

            value = self.code[self.pc]
            self._push(value)

            self.pc += 1
            return

        if opcode == OP_PUSH32:
            data = self.code[self.pc + 1 : self.pc + 33]
            if len(data) < 32:
                raise Exception("PUSH32 missing data")
            self.stack.append(bytes(data))  # type: ignore
            self.pc += 33
            return

        if opcode == OP_ADDRESS:
            self._push(self.address)
            return

        if opcode == OP_BALANCE:
            self._push(self.balance)
            return

        if opcode == OP_CODESIZE:
            self._push(len(self.code))
            return

        if opcode == OP_GASPRICE:
            self._push(self.gas_price)
            return

        if opcode == OP_BLOCKHASH:
            self._push(self.block_env["blockhash"])
            return

        if opcode == OP_TIMESTAMP:
            self._push(self.block_env["timestamp"])
            return

        if opcode == OP_NUMBER:
            self._push(self.block_env["number"])
            return

        if opcode == OP_GASLIMIT:
            self._push(self.block_env["gaslimit"])
            return

        if opcode == OP_BASEFEE:
            self._push(self.block_env["basefee"])
            return

        if opcode == OP_SELFBALANCE:
            self._push(self.balance)
            return

        if opcode == OP_STORE:
            key = self._pop()
            value = self._pop()
            self.storage[key] = value
            return

        if opcode == OP_LOAD:
            key = self._pop()
            value = self.storage.get(key)
            self._push(value)  # type: ignore
            return

        raise Exception(f"unknown opcode: {hex(opcode)}")

    def run(self) -> None:
        while not self.stopped and self.pc < len(self.code):
            self.step()

    def push_u256(self, value: int) -> list[int]:
        data = value.to_bytes(32, "big")
        return [OP_PUSH32] + list(data)

    def execute_transaction(self, tx: Transaction) -> None:
        total_cost = tx.calculate_gas_in_nim()
        if tx.sender == tx.recipient:
            return
        if self.balance < total_cost + tx.value:
            raise Exception("insufficient balance for gas + value")

        self.balance -= total_cost
        self.balance -= tx.value

        if tx.input_data and len(tx.input_data) > 0:
            self.load(tx.input_data, tx.gas)
            self.run()


def push_address(addr: bytes) -> list[int]:
    if not isinstance(addr, bytes):
        raise TypeError("address must be raw bytes")

    if len(addr) not in (20, 32):
        raise ValueError("address must be 20 or 32 bytes")

    return [OP_PUSH, len(addr), *addr]
