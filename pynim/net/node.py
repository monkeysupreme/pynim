import json
import socket
import threading
from pynim.net.peer import Peer


class Node:
    def __init__(
            self, 
            host: str = "0.0.0.0", 
            port: int = 4343
    ) -> None:
        self.host = host
        self.port = port
        self.peers: list[Peer] = []
        self.running: bool = False

    def start(self) -> None:
        self.running = True
        t = threading.Thread(target=self._listen)
        t.daemon = True
        t.start()

    def _listen(self) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()
        while self.running:
            conn, addr = server.accept()
            threading.Thread(target=self._handle_client,args=(conn,),daemon=True).start()

    def connect(self, host: str, port: int):
        peer = Peer(host, port)
        self.peers.append(peer)
        self._send(peer, {"type": "handshake", "port": self.port})

    def _handle_client(self, conn: socket.socket) -> None:
        while 1:
            data = conn.recv(4096)
            if not data:
                break
            try:
                msg = json.loads(data.decode())
                self._route(msg, conn)
            except:
                continue

    def _send(self, peer: Peer, msg: dict) -> None:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(peer.address)
            s.send(json.dumps(msg).encode())
            s.close()
        except:
            pass

    def broadcast(self, message: dict):
        for peer in self.peers:
            self._send(peer, message)

    def _route(self, msg: dict, conn: socket.socket):
        t = msg.get("type")
        if t == "handshake":
            self.peers.append(Peer(conn.getpeername()[0], msg["port"]))
            response = {"type": "handshake_ack", "port": self.port}
            conn.send(json.dumps(response).encode())
        if t == "handshake_ack":
            self.peers.append(Peer(conn.getpeername()[0], msg["port"]))
        if t == "block":
            self.on_block(msg["data"])
        if t == "transaction":
            self.on_transaction(msg["data"])

    def on_block(self, block_data: dict) -> None:
        print(block_data)

    def on_transaction(self, transaction_data: dict) -> None:
        print(transaction_data)