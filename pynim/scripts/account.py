from argparse import ArgumentParser

from pynim.account import Account


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("cmd", choices=["new", "load"])
    parser.add_argument("path", help="File path to account (.json)")

    args = parser.parse_args()

    if args.cmd == "new":
        account = Account(None, {}, public_key=None)
        account.generate_keys()
        account.save(args.path)
        print("\nAddress: ", account.address.hex())
    elif args.cmd == "load":
        account = Account.load(args.path)
        print(account.to_json(indent=4))
