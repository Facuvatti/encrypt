"""Codificación reversible de enteros y formato de ciphertext v2."""

import hmac
import struct

from cypher.cesar import UNICODE_SCALAR_COUNT


MAGIC = b"FCYP"
FORMAT_VERSION = 2

HEADER_PREFIX_STRUCT = struct.Struct(">4sBQ")
AUTH_TAG_SIZE = 32


def pack_ciphertext(
    plain_char_count: int,
    encrypted_body: str,
    auth_key: bytes,
) -> bytes:
    """Construye el contenedor v2 con autenticación HMAC-SHA256."""

    if not isinstance(plain_char_count, int) or plain_char_count < 0:
        raise ValueError("La longitud del texto debe ser un entero no negativo")

    if not isinstance(auth_key, bytes) or not auth_key:
        raise ValueError("auth_key debe ser bytes no vacíos")

    prefix = HEADER_PREFIX_STRUCT.pack(
        MAGIC,
        FORMAT_VERSION,
        plain_char_count
    )

    body = encrypted_body.encode("utf-8")

    tag = hmac.new(
        auth_key,
        prefix + body,
        "sha256"
    ).digest()

    return prefix + tag + body


def unpack_ciphertext(
    ciphertext: bytes,
    auth_key: bytes
) -> tuple[int, str]:
    """Valida cabecera y HMAC; devuelve longitud original y cuerpo cifrado."""

    if not isinstance(ciphertext, (bytes, bytearray, memoryview)):
        raise TypeError("El ciphertext debe ser bytes")

    if not isinstance(auth_key, bytes) or not auth_key:
        raise ValueError("auth_key debe ser bytes no vacíos")

    raw = bytes(ciphertext)

    minimum_size = HEADER_PREFIX_STRUCT.size + AUTH_TAG_SIZE

    if len(raw) < minimum_size:
        raise ValueError(
            "Ciphertext truncado: falta la cabecera o la autenticación"
        )

    magic, version, plain_char_count = HEADER_PREFIX_STRUCT.unpack_from(raw)

    if magic != MAGIC:
        raise ValueError(
            "Formato no reconocido: se esperaba un ciphertext FCYP"
        )

    if version != FORMAT_VERSION:
        raise ValueError(f"Versión no compatible: {version}")

    tag_start = HEADER_PREFIX_STRUCT.size
    tag_end = tag_start + AUTH_TAG_SIZE

    received_tag = raw[tag_start:tag_end]
    body = raw[tag_end:]
    prefix = raw[:tag_start]

    expected_tag = hmac.new(
        auth_key,
        prefix + body,
        "sha256"
    ).digest()

    if not hmac.compare_digest(received_tag, expected_tag):
        raise ValueError(
            "Autenticación fallida: clave incorrecta o ciphertext alterado"
        )

    try:
        encrypted_body = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "El cuerpo cifrado no contiene UTF-8 válido"
        ) from exc

    return plain_char_count, encrypted_body


def digits_required(char_count: int) -> int:
    """Dígitos base-N suficientes para cualquier fragmento de char_count chars.

    Cada escalar Unicode puede ocupar como máximo 4 bytes en UTF-8.
    El byte inicial adicional almacena la longitud exacta en bytes.
    """

    if not isinstance(char_count, int) or char_count < 1:
        raise ValueError("char_count debe ser un entero positivo")

    max_payload_bytes = 1 + 4 * char_count

    exclusive_limit = 1 << (8 * max_payload_bytes)

    width = 1
    capacity = UNICODE_SCALAR_COUNT

    while capacity < exclusive_limit:
        width += 1
        capacity *= UNICODE_SCALAR_COUNT

    return width


def int_to_base_digits(value: int, width: int) -> list[int]:
    """Representa value en exactamente width dígitos de base N, MSB primero."""

    if not isinstance(value, int) or value < 0:
        raise ValueError("value debe ser un entero no negativo")

    if not isinstance(width, int) or width < 1:
        raise ValueError("width debe ser un entero positivo")

    digits = [0] * width
    remaining = value

    for position in range(width - 1, -1, -1):
        remaining, digits[position] = divmod(
            remaining,
            UNICODE_SCALAR_COUNT
        )

    if remaining:
        raise OverflowError(
            "El entero no cabe en el ancho base-N solicitado"
        )

    return digits


def base_digits_to_int(digits: list[int]) -> int:
    """Reconstruye un entero a partir de dígitos base-N, MSB primero."""

    if not digits:
        raise ValueError("Se necesita al menos un dígito")

    value = 0

    for digit in digits:
        if (
            not isinstance(digit, int)
            or not 0 <= digit < UNICODE_SCALAR_COUNT
        ):
            raise ValueError("Dígito base-N fuera de rango")

        value = value * UNICODE_SCALAR_COUNT + digit

    return value


def fragment_to_int(fragment: str) -> int:
    """Convierte un fragmento a entero conservando también sus bytes iniciales nulos."""

    fragment_bytes = fragment.encode("utf-8")

    if len(fragment_bytes) > 255:
        raise ValueError(
            "El fragmento supera el límite de 255 bytes del prefijo"
        )

    payload = bytes((len(fragment_bytes),)) + fragment_bytes

    return int.from_bytes(payload, byteorder="big")


def int_to_fragment(value: int, expected_char_count: int) -> str:
    """Reconstruye el fragmento UTF-8 y valida su longitud en caracteres."""

    if not isinstance(value, int) or value < 0:
        raise ValueError(
            "El valor reconstruido debe ser un entero no negativo"
        )

    if value == 0:
        raise ValueError(
            "El valor reconstruido no contiene el prefijo de longitud"
        )

    raw = value.to_bytes(
        (value.bit_length() + 7) // 8,
        byteorder="big"
    )

    byte_count = raw[0]

    if byte_count != len(raw) - 1:
        raise ValueError(
            "Longitud interna del fragmento inconsistente"
        )

    try:
        fragment = raw[1:].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "El fragmento reconstruido no es UTF-8 válido"
        ) from exc

    if len(fragment) != expected_char_count:
        raise ValueError(
            "La longitud del fragmento reconstruido no coincide con la esperada"
        )

    return fragment