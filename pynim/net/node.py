import json
import logging
import socket
import threading

from typing import Tuple
from pynim.net.peer import Peer

logger = logging.getLogger()

def peer_address_tuple(peer: Peer) -> Tuple[str, int]:
    if hasattr(peer, "address") and isinstance(getattr(peer, "address"), tuple):
        return peer.address
    if hasattr(peer, "address") and callable(getattr(peer, "address")):
        return peer.address()
    if hasattr(peer, "host") and hasattr(peer, "port"):
        return (peer.host, peer.port)
    raise ValueError("Peer has no usable address/host/port")


class Node:
    def __init__(self, host: str = "0.0.0.0", port: int = 4343) -> None:
        self.host = host
        self.port = port
        self.peers: list[Peer] = []
        self.running: bool = False

    def start(self) -> None:
        self.running = True
        t = threading.Thread(target=self._listen, daemon=True)
        t.start()
        logger.info(f"Starting peer on {self.host}:{self.port}")

    def _listen(self) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen()
        while self.running:
            try:
                conn, addr = server.accept()
                logger.info(f"Listening for connections on {addr[0]}:{addr[1]}")
                threading.Thread(
                    target=self._handle_client, args=(conn,), daemon=True
                ).start()
            except Exception as e:
                logger.exception("Listen accept failed: %s", e)

    def connect(self, host: str, port: int):
        peer = Peer(host, port)
        self._send(peer, {"type": "handshake", "port": self.port})

    def _handle_client(self, conn: socket.socket) -> None:
        with conn:
            while True:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                    msg = json.loads(data.decode())
                    logger.info("Received raw msg: %s", msg)
                    self._route(msg, conn)
                except json.JSONDecodeError as e:
                    logger.error("JSON decode error: %s", e)
                    break
                except Exception as e:
                    logger.exception("Error handling client data: %s", e)
                    break

    def _send(self, peer: Peer, msg: dict) -> None:
        try:
            addr = peer_address_tuple(peer)
        except Exception as e:
            logger.error("Invalid peer address: %s (%s)", peer, e)
            return
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            s.connect(addr)
            s.send(json.dumps(msg).encode())
            try:
                resp = s.recv(4096)
                if resp:
                    logger.info("Got response from %s: %s", addr, resp.decode())
            except Exception:
                pass
            s.close()
            logger.info("Sent %s to %s", msg.get("type"), addr)
        except Exception as e:
            logger.exception("Failed to send to %s: %s", addr, e)

    def broadcast(self, message: dict):
        logger.info("Broadcasting %s to %d peers", message.get("type"), len(self.peers))
        for peer in list(self.peers):
            self._send(peer, message)

    def _route(self, msg: dict, conn: socket.socket):
        t = msg.get("type")
        if t == "handshake":
            peer_ip = conn.getpeername()[0]
            peer_port = msg["port"]
            new_peer = Peer(peer_ip, peer_port)
            if not any((p.host == new_peer.host and p.port == new_peer.port) if hasattr(p,'host') else False for p in self.peers):
                self.peers.append(new_peer)
                logger.info("Added peer %s:%s via handshake", peer_ip, peer_port)
            conn.send(json.dumps({"type": "handshake_ack", "port": self.port}).encode())
        elif t == "handshake_ack":
            peer_ip = conn.getpeername()[0]
            peer_port = msg["port"]
            new_peer = Peer(peer_ip, peer_port)
            if not any((p.host == new_peer.host and p.port == new_peer.port) if hasattr(p,'host') else False for p in self.peers):
                self.peers.append(new_peer)
                logger.info("Added peer %s:%s via handshake_ack", peer_ip, peer_port)
        elif t == "block":
            payload = msg.get("data")
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except Exception:
                    logger.error("Block payload is a string but not JSON")
            if not isinstance(payload, dict):
                logger.error("Block payload not a dict: %s", type(payload))
                return
            self.on_block(payload)
        elif t == "transaction":
            payload = msg.get("data")
            self.on_transaction(payload)
        else:
            logger.warning("Unknown message type: %s", t)

    def on_block(self, block_data: dict) -> None:
        logger.info(
            "BLOCK RECEIVED\n\t"
            "time=%s\n\t"
            "hash=%s...\n\t"
            "txs=%s",
            block_data.get("header", {}).get("timestamp") or block_data.get("timestamp"),
            (block_data.get("cached_hash") or block_data.get("hash", b""))[:10] if isinstance(block_data.get("cached_hash") or block_data.get("hash"), (bytes, bytearray)) else str(block_data.get("cached_hash") or block_data.get("hash", ""))[:10],
            len(block_data.get("transactions") or block_data.get("txs") or [])
        )

    def on_transaction(self, transaction_data: dict) -> None:
        logger.info("TX RECEIVED: %s", transaction_data)

