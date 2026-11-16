# Encrypt

**An experimental text-encryption project exploring deterministic randomness, mathematical functions, and reversible transformations.**

Encrypt is a Python research project that experiments with a custom text-transformation pipeline. It combines a Weierstrass function, a deterministic SHA-256-based pseudorandom generator, Unicode-aware transformations, and a versioned binary ciphertext container.

> [!WARNING]
> **Experimental software — not suitable for protecting real secrets.** This project implements a custom cryptographic design that has not been independently reviewed or audited. Do not use it for passwords, private messages, sensitive files, or production systems. Prefer established, audited cryptographic libraries and protocols for real-world security.

## What it explores

- **Weierstrass-based parameter sequences** to derive variable split and fragment sizes.
- **Deterministic pseudorandomness** using SHA-256 and reproducible seeds.
- **Text fragmentation and shuffling** to experiment with reversible data transformations.
- **Unicode-aware encoding** that maps valid Unicode scalar values into a modular alphabet.
- **A versioned ciphertext format (FCYP v2)** with a header, original character count, encrypted body, and HMAC-SHA256 integrity check.

## Project structure

```text
encrypt/
├── cipher/
│   ├── cesar.py          # Unicode-aware Caesar transformations
│   ├── codec.py          # Integer/fragment encoding and FCYP v2 container
│   └── dict_text.py      # Text-to-position dictionary helper
├── encrypt.py            # Encryption entry point
├── decrypt.py            # Decryption entry point
├── generate_corpus.py    # Random corpus generation for experiments
├── rng.py                # Deterministic SHA-256-based PRNG
├── utils.py              # Integer splitting helpers
├── weierstrass.py        # Weierstrass function and normalization
└── requirements.txt      # Python dependencies
```

## Requirements

- Python 3.10 or newer
- NumPy

Install the dependency with:

```bash
python -m pip install -r requirements.txt
```

## Current status

The repository is a work in progress. The encryption and decryption flow is being developed, and the current source contains inconsistent module imports (including `cipher.cesar`, `cypher.cesar`, and the actual `cipher/cesar.py` path). As a result, the command-line workflow may fail before running.

The corpus-generation script is intended for experiments and currently writes to `./pruebas/salida2.bin`; that output directory must exist before running it. The script also invokes the encryption routine repeatedly and is not a ready-made benchmark or security test suite.

## Security notes

- A custom cipher is not considered secure merely because it uses SHA-256, HMAC, Unicode transformations, or complicated mathematical functions.
- The deterministic seed is derived from the supplied parameters. Those parameters should not be treated as a substitute for a cryptographically secure secret key.
- HMAC can detect modifications when its key remains secret, but it does not make an unreviewed encryption construction secure.
- No independent cryptographic audit, formal security proof, or production-readiness claim is made for this project.

## Goals

This repository is primarily a space for learning and experimentation with:

1. Reversible transformations of text and Unicode data.
2. Deterministic pseudorandom sequences.
3. Mathematical functions as inputs to algorithmic processes.
4. Binary serialization and integrity validation.
5. Testing and evaluating a custom encryption design.

## Contributing

Suggestions, bug reports, and constructive reviews are welcome. If you work on the cryptographic design, please include reproducible tests and clearly document any security assumptions.

## License

No license has been added yet. Until a license is provided, the repository's code is not automatically granted permission for reuse, distribution, or modification.
