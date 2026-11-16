import hashlib
class HashRNG:
    """
    Generador pseudoaleatorio reproducible basado en SHA-256.
    Misma semilla -> misma secuencia, siempre.
    """

    def __init__(self, seed_bytes):
        self._seed = seed_bytes
        self._counter = 0
        self._buffer = b""

    def _refill(self):
        h = hashlib.sha256()
        h.update(self._seed)
        h.update(self._counter.to_bytes(16, "little"))
        self._buffer = h.digest()
        self._counter += 1

    def next_uint64(self):
        if len(self._buffer) < 8:
            self._refill()
        chunk = self._buffer[:8]
        self._buffer = self._buffer[8:]
        return int.from_bytes(chunk, "little")

    def random(self):
        """Float en [0, 1)."""
        return self.next_uint64() / 2**64

    def randint(self, a, b):
        """Entero en [a, b] inclusive."""
        if b < a:
            raise ValueError("b debe ser >= a")
        span = b - a + 1
        # Rejection sampling para evitar sesgo
        limit = (2**64 // span) * span
        while True:
            r = self.next_uint64()
            if r < limit:
                return a + (r % span)

    def choice(self, seq):
        return seq[self.randint(0, len(seq) - 1)]

    def shuffle(self, seq):
        """Fisher-Yates determinístico."""
        for i in range(len(seq) - 1, 0, -1):
            j = self.randint(0, i)
            seq[i], seq[j] = seq[j], seq[i]

def make_seed(a, b, offset):
    """Hash estable de los parámetros del algoritmo."""
    h = hashlib.sha256()
    h.update(repr(float(a)).encode("utf-8"))
    h.update(b"\x00")
    h.update(repr(int(b)).encode("utf-8"))
    h.update(b"\x00")
    h.update(repr(int(offset)).encode("utf-8"))
    return h.digest()
