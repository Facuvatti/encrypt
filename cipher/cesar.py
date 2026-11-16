"""Cifrado César reversible sobre los escalares Unicode válidos."""

UNICODE_LIMIT = 0x110000
SURROGATE_START = 0xD800
SURROGATE_END = 0xDFFF
SURROGATE_COUNT = SURROGATE_END - SURROGATE_START + 1
UNICODE_SCALAR_COUNT = UNICODE_LIMIT - SURROGATE_COUNT


def _scalar_to_index(char: str) -> int:
    """Mapea un escalar Unicode a [0, UNICODE_SCALAR_COUNT)."""
    if len(char) != 1:
        raise ValueError("Se esperaba exactamente un carácter")

    code = ord(char)

    if SURROGATE_START <= code <= SURROGATE_END:
        raise ValueError("Los sustitutos Unicode no son escalares válidos")

    if code > SURROGATE_END:
        return code - SURROGATE_COUNT

    return code


def _index_to_scalar(index: int) -> str:
    """Mapea un índice del alfabeto de escalares Unicode a un carácter."""
    if not isinstance(index, int):
        raise TypeError("El índice debe ser un entero")

    index %= UNICODE_SCALAR_COUNT

    if index >= SURROGATE_START:
        index += SURROGATE_COUNT

    return chr(index)


def universal_caesar_cipher(text: str, shift: int) -> str:
    """Desplaza cada carácter dentro del alfabeto Unicode sin colisiones."""
    if not isinstance(text, str):
        raise TypeError("text debe ser str")

    if not isinstance(shift, int):
        raise TypeError("shift debe ser int")

    shift %= UNICODE_SCALAR_COUNT

    return "".join(
        _index_to_scalar(_scalar_to_index(char) + shift)
        for char in text
    )


def universal_caesar_decipher(text: str, shift: int) -> str:
    """Invierte exactamente universal_caesar_cipher."""
    if not isinstance(text, str):
        raise TypeError("text debe ser str")

    if not isinstance(shift, int):
        raise TypeError("shift debe ser int")

    shift %= UNICODE_SCALAR_COUNT

    return "".join(
        _index_to_scalar(_scalar_to_index(char) - shift)
        for char in text
    )


def caesar_shift_between(original_char: str, encrypted_char: str) -> int:
    """Recupera el desplazamiento modular entre dos escalares Unicode."""
    original_index = _scalar_to_index(original_char)
    encrypted_index = _scalar_to_index(encrypted_char)

    return (encrypted_index - original_index) % UNICODE_SCALAR_COUNT