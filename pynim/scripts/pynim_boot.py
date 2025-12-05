import time

from pynim.account import Account
from pynim.blockchain import Blockchain
from pynim.genesis import GenesisBlock
from pynim.net.logger import init_logging
from pynim.net.node import Node


def main() -> None:
    init_logging()

    node1 = Node(port=4040)
    node2 = Node(port=5042)

    node1.start()
    node2.start()

    node1.connect("127.0.0.1", 5042)

    time.sleep(1)

    gb = GenesisBlock(current_time=int(time.time()), account=Account.load("account.json"))

    node1.broadcast({"type": "block", "data": gb.to_dict()})

    while True:
        time.sleep(1)
