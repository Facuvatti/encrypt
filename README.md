# Encrypt

**An experimental text-encryption project exploring deterministic randomness, mathematical functions, and reversible transformations.**

Encrypt is a Python research project that experiments with a custom text-transformation pipeline. It combines a Weierstrass function, a deterministic SHA-256-based pseudorandom generator, Unicode-aware transformations, and a versioned binary ciphertext container.

> [!WARNING]
> **Experimental software — not suitable for protecting real secrets.** This custom cryptographic design has not been independently reviewed or audited. Do not use it for passwords, private messages, sensitive files, or production systems. Prefer established, audited cryptographic libraries and protocols for real-world security.

## Download standalone programs

The automated release workflow builds standalone archives for Windows, macOS, and Linux and attaches them to the [GitHub Releases page](https://github.com/Facuvatti/encrypt/releases) when a version tag is pushed.

Each archive contains two standalone programs:
- `encrypt` / `encrypt.exe`: encrypts text and prints the FCYP v2 ciphertext in Base64.
- `decrypt` / `decrypt.exe`: accepts that Base64 ciphertext and prints the recovered text.

Python and NumPy are bundled; users do not need to install Python.

### Quick start

1. Download the archive for your operating system from [Releases](https://github.com/Facuvatti/encrypt/releases).
2. Extract it and open a terminal in that folder.
3. Encrypt:

```bash
./encrypt --text "Texto para probar" --a 0.5 --b 3 --offset 1
```

On Windows, run `encrypt.exe`.

Copy the Base64 value printed between `=== CIPHERTEXT BASE64 ===` and `=== FIN ===`, then decrypt:

```bash
./decrypt --ciphertext "PEGAR_BASE64_AQUI" --a 0.5 --b 3 --offset 1
```

On Windows, run `decrypt.exe`. Use exactly the same `a`, `b`, and `offset` values for both commands. A nonzero offset that is a multiple of 100 is not accepted.

### Available release archives

| Platform | Archive |
| --- | --- |
| Windows x64 | `encrypt-windows-x64.zip` |
| Linux x64 | `encrypt-linux-x64.zip` |
| macOS Intel (x64) | `encrypt-macos-x64.zip` |
| macOS Apple Silicon (ARM64) | `encrypt-macos-arm64.zip` |

A release is created automatically when a version tag matching `v*` is pushed. The build workflow runs regression tests before packaging the executables.

## What it explores

- **Weierstrass-based parameter sequences** to derive variable split and fragment sizes.
- **Deterministic pseudorandomness** using SHA-256 and reproducible seeds.
- **Text fragmentation and shuffling** to experiment with reversible data transformations.
- **Unicode-aware encoding** that maps valid Unicode scalar values into a modular alphabet.
- **A versioned ciphertext format (FCYP v2)** with a header, original character count, encrypted body, and HMAC-SHA256 integrity check.

## Project structure

```text
encrypt/
├── .github/workflows/
│   ├── ci.yml
│   └── release.yml
├── cipher/
│   ├── cesar.py
│   ├── codec.py
│   └── dict_text.py
├── tests/
│   └── test_roundtrip.py
├── decrypt.py
├── encrypt.py
├── generate_corpus.py
├── RELEASE_NOTES.txt
├── requirements.txt
├── rng.py
├── utils.py
└── weierstrass.py
```

## Run from source

Requirements: Python 3.10 or newer and NumPy.

```bash
python -m pip install -r requirements.txt
python encrypt.py --text "Texto para probar" --a 0.5 --b 3 --offset 1
python decrypt.py --ciphertext "PEGAR_BASE64_AQUI" --a 0.5 --b 3 --offset 1
```

Run the regression tests with:

```bash
python -m unittest discover -s tests -v
```

## Security notes

- A custom cipher is not considered secure merely because it uses SHA-256, HMAC, Unicode transformations, or complicated mathematical functions.
- The deterministic seed is derived from the supplied parameters. Those parameters are not a substitute for a cryptographically secure secret key.
- HMAC can detect modifications when its key remains secret, but it does not make an unreviewed encryption construction secure.
- No independent cryptographic audit, formal security proof, or production-readiness claim is made for this project.

## License

No license has been added yet. Until a license is provided, the repository's code is not automatically granted permission for reuse, distribution, or modification.
