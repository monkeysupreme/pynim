import time

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

    node1.broadcast({"type": "tx", "data": "hello world"})
    node2.broadcast({"type": "block", "data": "new-block-123"})

    while True:
        time.sleep(1)
