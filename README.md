# solana-brute-force-using-python
a solana keypair generator mainnet and balance checker on python 
# Solana Account Scanner

A Python script that demonstrates how to interact with the Solana blockchain by randomly generating keypairs and checking their balances.

## Disclaimer

This tool is for educational purposes only. The probability of finding a funded account through random generation is astronomically low (1 in 2^256).

## Features

- Generates random Solana keypairs
- Checks account balances on the Solana mainnet
- Provides detailed logging of RPC interactions
- Implements rate limiting to avoid API restrictions
- Displays colorful terminal output with statistics

## Requirements

- Python 3.7+
- solana
- solders
- colorama

## Installation

```
pip install -r requirements.txt
```

## Usage

```
python sol.py
```

Press Ctrl+C to stop the script at any time.

## How It Works

The script connects to the Solana mainnet through a public RPC endpoint and:

1. Generates random keypairs
2. Checks if the corresponding account has any balance
3. Displays statistics about the process
4. Reports any funded accounts found (extremely unlikely)

## Educational Value

This script demonstrates:
- How to interact with the Solana blockchain using Python
- The security of cryptographic systems (finding a random funded account is virtually impossible)
- How to handle RPC responses and errors
- Basic rate limiting techniques

