import os
import time
from argparse import ArgumentParser

from pynim.account import Account
from pynim.genesis import GenesisBlock


def generate_genesis(account_path: str) -> GenesisBlock:
    return GenesisBlock(int(time.time()), Account.load(account_path))


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--datadir", help="Directory with the blockchain data")
    parser.add_argument("path", help="Genesis file path (default: genesis.json)")

    args = parser.parse_args()

    os.mkdir(args.datadir)

    with open(os.path.join(args.datadir, args.path), "w") as f:
        gb = generate_genesis("account.json")
        f.write(gb.to_json(indent=4))
