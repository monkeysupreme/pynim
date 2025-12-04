Understood — your clipboard is likely breaking because the README is wrapped in a block *inside* a block.
Below is the **FINAL README.md with NO outer formatting — 100% copy-and-paste clean.**

---

# 🐍 pynim — A Python-based Blockchain Implementation

`pynim` is a lightweight blockchain written in Python.
It focuses on clarity, modular design, and minimal components needed to initialize a blockchain, generate accounts, and boot a local node.

This project is experimental and under active development — contributions are welcome.

---

## 🚀 Features

* Pure Python blockchain
* JSON account/keystore generation
* Genesis initialization with configurable state
* Bootable node for local operation
* CLI-driven command execution
* Simple architecture — great for learning or extending

---

## 📦 Installation

```bash
git clone https://github.com/monkeysupreme/pynim
cd pynim
pip install -e .
```

> Uses `pyproject.toml` only — no `setup.py` required.

---

## 🧰 CLI Commands

### 🔑 Create an account

```
pynim-account new <account_name>.json
```

**Example:**

```
pynim-account new alice.json
```

Creates a new keypair and saves it to a keystore JSON file.

---

### 🏗 Initialize a blockchain

```
pynim-init --datadir <data_dir> <genesis_file>.json
```

**Example:**

```
pynim-init --datadir chain0 genesis.json
```

Initializes a new blockchain directory with genesis state.

---

### 🚀 Boot the blockchain node

```
pynim-boot --datadir <data_dir>
```

**Example:**

```
pynim-boot --datadir chain0
```

Starts the node and loads chain state for operation.

---

## 🧪 Example Workflow

```bash
# 1. Create an account
pynim-account new miner.json

# 2. Initialize blockchain with genesis
pynim-init --datadir chain0 genesis.json

# 3. Boot the node
pynim-boot --datadir chain0
```

---

## 📂 Project Structure

```
pynim/
 ├── account.py          # Account + keystore handling
 ├── block.py            # Block format + hashing + validation
 ├── chain.py            # Chain state, block management
 ├── crypto.py           # Hashing + cryptographic utilities
 ├── genesis.py          # Genesis loader
 ├── cli/                # CLI entry command routing
 └── ...

pyproject.toml            # Packaging + CLI entrypoints
README.md                 # This file
```

---

## 🔧 Development

Format code (if format script exists):

```bash
./format_pynim.sh
```

Run tests:

```bash
pytest -q
```

---

## 🧭 Roadmap

* P2P networking
* Mining / consensus (PoW or PoS)
* Transaction pool + mempool
* RPC API layer
* Smart contract VM execution

---

## 🤝 Contributing

PRs, issues, and ideas are welcomed!

1. Fork repo
2. Create branch
3. Commit changes
4. Open Pull Request

---

## 📄 License

MIT — free to use and modify.

---

