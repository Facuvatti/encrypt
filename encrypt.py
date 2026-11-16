import argparse
import base64

import numpy as np

from cipher.cesar import universal_caesar_cipher

from cipher.codec import (
    digits_required,
    fragment_to_int,
    int_to_base_digits,
    pack_ciphertext,
)

from rng import HashRNG, make_seed
from utils import split_into_parts
from weierstrass import normalize, weierstrass


def cipher(text: str, a: float, b: int, offset: int) -> bytes:
    """Cifra texto con el esquema Weierstrass + HashRNG (formato v2)."""

    if not isinstance(text, str):
        raise TypeError("text debe ser str")

    if not isinstance(b, int):
        raise TypeError("b debe ser int")

    if offset % 100 == 0 and offset != 0:
        raise ValueError("offset no puede ser múltiplo de 100")

    letters = [chr(i) for i in range(32, 256)]

    seed = make_seed(a, b, offset)

    rng_positions = HashRNG(seed + b"|positions")
    rng_letters = HashRNG(seed + b"|letters")

    # Split por longitudes variables basadas en Weierstrass

    _split_w = weierstrass(
        np.arange(1, len(text) + 2, dtype=float),
        a,
        b,
        n_max=18,
        x_offset=offset
    )

    _split_min, _split_max = (
        float(np.min(_split_w)),
        float(np.max(_split_w))
    )

    words = []

    _i = _k = 0

    while _i < len(text):
        _n = int(round(
            normalize(_split_w[_k], _split_min, _split_max, 3, 12)
        ))

        words.append(text[_i:_i + _n])

        _i += _n
        _k += 1

    rng_words = HashRNG(seed + b"|words")

    rng_words.shuffle(words)
    rng_letters.shuffle(letters)

    total_chars = sum(len(word) for word in words)

    total_points = total_chars * 6 + len(words) + 10

    max_val = total_points * 30

    candidates = list(range(3, max_val + 1, 3))

    pool = candidates[:]

    n_pick = min(total_points, len(pool))

    for i in range(n_pick):
        j = rng_positions.randint(i, len(pool) - 1)

        pool[i], pool[j] = pool[j], pool[i]

    pool = pool[:n_pick]

    rng_positions.shuffle(pool)

    indices = np.array(
        [float(p) + rng_positions.random() for p in pool],
        dtype=float
    )

    raw_weierstrass = weierstrass(
        indices,
        a,
        b,
        n_max=18,
        x_offset=offset
    )

    w_min = np.min(raw_weierstrass)
    w_max = np.max(raw_weierstrass)

    cursor = 0

    def next_value():
        nonlocal cursor

        if cursor >= len(raw_weierstrass):
            raise RuntimeError(
                "Se agotaron los valores Weierstrass"
            )

        value = raw_weierstrass[cursor]

        cursor += 1

        return value

    result_words = []

    for word in words:

        val = next_value()

        max_width = max(1, len(word) // 2)

        width = int(round(
            normalize(val, w_min, w_max, 1, max_width)
        ))

        width = max(1, width)

        fragments = [
            word[i:i + width]
            for i in range(0, len(word), width)
        ]

        encrypted_word = []

        for fragment in fragments:

            val = next_value()

            noise_amount = int(round(
                normalize(val, w_min, w_max, 1, 5)
            ))

            noise_amount = max(1, min(5, noise_amount))

            # Transformación del fragmento a entero reversible.

            hide = fragment_to_int(fragment)

            # Se utiliza val como semilla, tal como corregiste.
            # No se modifica split_into_parts ni utils.py.

            parts = split_into_parts(
                hide,
                val,
                noise_amount
            )

            # Cantidad fija de dígitos para este fragmento.

            digit_count = digits_required(len(fragment))

            chars = []

            previous = None

            for part in parts:

                digits = int_to_base_digits(
                    part,
                    digit_count
                )

                for digit in digits:

                    letter = rng_letters.choice(letters)

                    while letter == previous:
                        letter = rng_letters.choice(letters)

                    position = rng_letters.randint(
                        0,
                        len(chars)
                    )

                    chars.insert(
                        position,
                        universal_caesar_cipher(letter, digit)
                    )

                    previous = letter

            encrypted_word.append("".join(chars))

        result_words.append("".join(encrypted_word))

    result = "".join(result_words)
    body = result.encode("utf-8")
    # Formato binario versionado y autenticado.

    ciphertext = pack_ciphertext(
        len(text),
        body,
        seed + b"|auth"
    )

    print("=== CIPHERTEXT BASE64 ===")

    print(
        base64.b64encode(ciphertext).decode("ascii")
    )

    print("=== FIN ===")

    return ciphertext, body


example = "Podes escribir lo que sea y nadie lo va a encontrar muajajjaa"


def main():

    parser = argparse.ArgumentParser(
        description="Cifra texto con el formato FCYP v2"
    )

    parser.add_argument(
        "-text",
        "-t",
        type=str,
        default=example
    )

    parser.add_argument(
        "-a",
        type=float,
        required=True
    )

    parser.add_argument(
        "-b",
        type=int,
        required=True
    )

    parser.add_argument(
        "-offset",
        "-o",
        type=int,
        required=True
    )

    args = parser.parse_args()

    cipher(
        args.text,
        args.a,
        args.b,
        args.offset
    )


if __name__ == "__main__":
    main()