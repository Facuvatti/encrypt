import numpy as np
import random
from pseudorandom import make_seed, HashRNG
from weierstrass import weierstrass, normalize

def cifrar(text: str, a: float, b: int, offset: int) -> bytes:
    """
    Cifra `text` usando el esquema basado en Weierstrass + HashRNG.

    Parámetros
    ----------
    text : str
        Texto plano a cifrar.
    a : float
        Parámetro `a` de la función de Weierstrass.
    b : int
        Parámetro `b` de la función de Weierstrass.
    offset : int
        Desplazamiento `x_offset` usado en Weierstrass.

    Devuelve
    --------
    bytes
        Ciphertext en bytes (codificación latin-1).
    """
    # Lista de letras (se reordena con el RNG por semilla, así que debe
    # construirse localmente para no depender de estado global).
    letters = [chr(i) for i in range(32, 256)]

    msg = text

    seed = make_seed(a, b, offset)
    rng_positions = HashRNG(seed + b"|positions")
    rng_letters = HashRNG(seed + b"|letters")

    # Split por longitudes variables basadas en Weierstrass
    _split_w = weierstrass(
        np.arange(1, len(msg) + 2, dtype=float),
        a, b, n_max=18, x_offset=offset
    )
    _split_min, _split_max = float(np.min(_split_w)), float(np.max(_split_w))

    words = []
    _i = _k = 0
    while _i < len(msg):
        _n = int(round(normalize(_split_w[_k], _split_min, _split_max, 3, 12)))
        words.append(msg[_i:_i + _n])
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
        indices, a, b,
        n_max=18, x_offset=offset
    )

    w_min = np.min(raw_weierstrass)
    w_max = np.max(raw_weierstrass)

    cursor = 0

    def next_value():
        nonlocal cursor
        value = raw_weierstrass[cursor]
        cursor += 1
        return value

    result_words = []

    for word in words:
        val = next_value()

        max_width = max(1, len(word) // 2)
        width = int(round(normalize(val, w_min, w_max, 1, max_width)))

        fragments = [
            word[i:i + max(1, width)]
            for i in range(0, len(word), max(1, width))
        ]

        encrypted_word = []

        for fragment in fragments:
            val = next_value()
            noise_amount = int(round(normalize(val, w_min, w_max, 1, 5)))

            chars = list(fragment)
            previous = None

            for _ in range(noise_amount):
                letter = rng_letters.choice(letters)
                while letter == previous:
                    letter = rng_letters.choice(letters)

                position = rng_letters.randint(0, len(chars))
                chars.insert(position, letter)
                previous = letter

            # Sufijo: cantidad y letras con pseudoaleatoriedad independiente
            suffix_val = next_value()
            suffix_amount = int(round(normalize(suffix_val, w_min, w_max, 1, 5)))
            previous = None
            for _ in range(suffix_amount):
                letter = rng_letters.choice(letters)
                while letter == previous:
                    letter = rng_letters.choice(letters)
                chars.append(letter)
                previous = letter

            encrypted_word.append("".join(chars))

        result_words.append("".join(encrypted_word))

    result = "".join(result_words)
    return result.encode("latin-1")