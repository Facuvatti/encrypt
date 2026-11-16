import argparse
import base64
import binascii

import numpy as np

from cipher.cesar import caesar_shift_between

from cipher.codec import (
    base_digits_to_int,
    digits_required,
    int_to_fragment,
    unpack_ciphertext,
)

from rng import HashRNG, make_seed
from weierstrass import normalize, weierstrass


def _decode_base64_if_needed(ciphertext: bytes | str) -> bytes:
    if isinstance(ciphertext, str):

        try:
            return base64.b64decode(
                ciphertext,
                validate=True
            )

        except (binascii.Error, ValueError) as exc:
            raise ValueError(
                "El ciphertext de texto debe estar en Base64 válido"
            ) from exc

    if isinstance(ciphertext, (bytes, bytearray, memoryview)):
        return bytes(ciphertext)

    raise TypeError(
        "ciphertext debe ser bytes o una cadena Base64"
    )


def decipher(
    ciphertext: bytes | str,
    a: float,
    b: int,
    offset: int
) -> str:
    """Descifra un ciphertext v2 producido por encriptar.cypher."""

    if not isinstance(b, int):
        raise TypeError("b debe ser int")

    if offset % 100 == 0 and offset != 0:
        raise ValueError("offset no puede ser múltiplo de 100")

    raw_ciphertext = _decode_base64_if_needed(ciphertext)

    seed = make_seed(a, b, offset)

    plain_char_count, encrypted_body = unpack_ciphertext(
        raw_ciphertext,
        seed + b"|auth"
    )

    if plain_char_count == 0:

        if encrypted_body:
            raise ValueError(
                "El texto original era vacío, pero el cuerpo no lo es"
            )

        return ""

    rng_positions = HashRNG(seed + b"|positions")
    rng_letters = HashRNG(seed + b"|letters")

    # Reconstrucción de las longitudes originales.

    _split_w = weierstrass(
        np.arange(1, plain_char_count + 2, dtype=float),
        a,
        b,
        n_max=18,
        x_offset=offset
    )

    _split_min = float(np.min(_split_w))
    _split_max = float(np.max(_split_w))

    word_lengths = []

    _i = _k = 0

    while _i < plain_char_count:

        _n = int(round(
            normalize(
                _split_w[_k],
                _split_min,
                _split_max,
                3,
                12
            )
        ))

        word_length = min(
            _n,
            plain_char_count - _i
        )

        word_lengths.append(word_length)

        _i += _n
        _k += 1

    # Reconstrucción del orden pseudoaleatorio de las palabras.

    word_order = list(range(len(word_lengths)))

    rng_words = HashRNG(seed + b"|words")

    rng_words.shuffle(word_order)

    # Reconstrucción del conjunto de caracteres.

    letters = [chr(i) for i in range(32, 256)]

    rng_letters.shuffle(letters)

    # Reconstrucción de los puntos de Weierstrass.

    total_chars = sum(word_lengths)

    total_points = (
        total_chars * 6 + len(word_lengths) + 10
    )

    max_val = total_points * 30

    candidates = list(range(3, max_val + 1, 3))

    pool = candidates[:]

    n_pick = min(total_points, len(pool))

    for i in range(n_pick):

        j = rng_positions.randint(
            i,
            len(pool) - 1
        )

        pool[i], pool[j] = pool[j], pool[i]

    pool = pool[:n_pick]

    rng_positions.shuffle(pool)

    indices = np.array(
        [
            float(p) + rng_positions.random()
            for p in pool
        ],
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
            raise ValueError(
                "Ciphertext o parámetros inconsistentes: RNG agotado"
            )

        value = raw_weierstrass[cursor]

        cursor += 1

        return value

    body_cursor = 0

    plaintext_words = [None] * len(word_lengths)

    # Procesamiento en el orden cifrado de las palabras.

    for original_word_index in word_order:

        word_length = word_lengths[original_word_index]

        val = next_value()

        max_width = max(1, word_length // 2)

        width = int(round(
            normalize(
                val,
                w_min,
                w_max,
                1,
                max_width
            )
        ))

        width = max(1, width)

        fragment_lengths = [
            min(width, word_length - start)
            for start in range(0, word_length, width)
        ]

        plaintext_fragments = []

        for fragment_length in fragment_lengths:

            val = next_value()

            noise_amount = int(round(
                normalize(
                    val,
                    w_min,
                    w_max,
                    1,
                    5
                )
            ))

            noise_amount = max(
                1,
                min(5, noise_amount)
            )

            digit_count = digits_required(
                fragment_length
            )

            symbol_count = noise_amount * digit_count

            encrypted_symbols = encrypted_body[
                body_cursor:body_cursor + symbol_count
            ]

            if len(encrypted_symbols) != symbol_count:
                raise ValueError(
                    "Ciphertext truncado: faltan símbolos de un fragmento"
                )

            body_cursor += symbol_count

            # Reproduce exactamente las inserciones aleatorias realizadas
            # al cifrar.

            insertion_order = []

            previous = None

            for part_index in range(noise_amount):

                for digit_index in range(digit_count):

                    letter = rng_letters.choice(letters)

                    while letter == previous:
                        letter = rng_letters.choice(letters)

                    position = rng_letters.randint(
                        0,
                        len(insertion_order)
                    )

                    insertion_order.insert(
                        position,
                        (
                            part_index,
                            digit_index,
                            letter
                        )
                    )

                    previous = letter

            # Cada parte tiene una representación de ancho fijo.

            digits_by_part = [
                [None] * digit_count
                for _ in range(noise_amount)
            ]

            # Recuperación de cada dígito mediante la diferencia César.

            for encrypted_char, (
                part_index,
                digit_index,
                original_letter
            ) in zip(encrypted_symbols, insertion_order):

                digits_by_part[part_index][digit_index] = (
                    caesar_shift_between(
                        original_letter,
                        encrypted_char
                    )
                )

            # Reconstrucción de los enteros originales.

            parts = [
                base_digits_to_int(digits)
                for digits in digits_by_part
            ]

            hide = sum(parts)

            # Reconstrucción del fragmento UTF-8.

            fragment = int_to_fragment(
                hide,
                fragment_length
            )

            plaintext_fragments.append(fragment)

        plaintext_words[original_word_index] = (
            "".join(plaintext_fragments)
        )

    # Verificación de que no sobren símbolos.

    if body_cursor != len(encrypted_body):

        raise ValueError(
            "El ciphertext contiene símbolos sobrantes: "
            "clave incorrecta o datos alterados"
        )

    # Restauración del orden original de las palabras.

    plaintext = "".join(plaintext_words)

    if len(plaintext) != plain_char_count:

        raise ValueError(
            "La longitud final no coincide con la indicada en la cabecera"
        )

    return plaintext


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Desencripta un ciphertext FCYP v2"
    )

    parser.add_argument(
        "-ciphertext",
        "--ciphertext",
        "-c",
        required=True,
        help="Ciphertext en Base64"
    )

    parser.add_argument(
        "-a",
        "--a",
        type=float,
        required=True
    )

    parser.add_argument(
        "-b",
        "--b",
        type=int,
        required=True
    )

    parser.add_argument(
        "-offset",
        "--offset",
        "-o",
        type=int,
        required=True
    )

    args = parser.parse_args()

    print(
        decipher(
            args.ciphertext,
            args.a,
            args.b,
            args.offset
        )
    )