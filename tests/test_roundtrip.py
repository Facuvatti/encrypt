import unittest

from cipher.cesar import universal_caesar_cipher, universal_caesar_decipher
from cipher.codec import pack_ciphertext, unpack_ciphertext
from decrypt import decipher
from encrypt import cipher


class CaesarTests(unittest.TestCase):
    def test_unicode_round_trip(self):
        original = "Hola, mundo! ñ 🧪 𝄞"
        encrypted = universal_caesar_cipher(original, 987654321)
        self.assertEqual(universal_caesar_decipher(encrypted, 987654321), original)


class ContainerTests(unittest.TestCase):
    def test_pack_unpack(self):
        key = b"test-auth-key"
        body = "cuerpo cifrado".encode("utf-8")
        packed = pack_ciphertext(12, body, key)
        self.assertEqual(unpack_ciphertext(packed, key), (12, body.decode()))

    def test_tampering_is_rejected(self):
        key = b"test-auth-key"
        packed = bytearray(pack_ciphertext(3, b"abc", key))
        packed[-1] ^= 1
        with self.assertRaisesRegex(ValueError, "Autenticación fallida"):
            unpack_ciphertext(packed, key)


class CipherRoundTripTests(unittest.TestCase):
    def test_empty_text(self):
        encrypted, _ = cipher("", 0.5, 3, 1)
        self.assertEqual(decipher(encrypted, 0.5, 3, 1), "")

    def test_ascii_and_unicode_text(self):
        for original in (
            "Texto corto de prueba",
            "Español: acción, pingüino y corazón",
            "Unicode: 🧪 🚀 𝄞 漢字",
        ):
            with self.subTest(original=original):
                encrypted, _ = cipher(original, 0.5, 3, 1)
                self.assertEqual(decipher(encrypted, 0.5, 3, 1), original)


if __name__ == "__main__":
    unittest.main()
