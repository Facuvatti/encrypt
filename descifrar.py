"""
Descifrador del cifrado Weierstrass + HashRNG (tolera textwrap con espacios).

Reutiliza las funciones del cifrador (ajustá los dos imports a tus módulos):
  - HashRNG, make_seed          -> módulo del PRNG
  - weierstrass, normalize      -> módulo de la función de Weierstrass

Uso:
  python descifrar.py -c "<base64>" -a 1.234 -b 7 -o 123
  python descifrar.py -c "<hex>" --hex -a 1.234 -b 7 -o 123

Nota: textwrap.wrap descarta espacios al borde de cada fragmento, así que esa
información se pierde al cifrar. El descifrador recupera todos los demás
caracteres con exactitud y reconstruye los espacios perdidos de la mejor
forma posible. Para recuperación exacta, en el cifrador reemplazá textwrap por
    fragments = [word[i:i+w] for i in range(0, len(word), w)]   # w = max(1, width)
"""
import argparse
import base64
import copy
import sys

import numpy as np

from pseudorandom import HashRNG, make_seed                  # <-- ajustar nombre del módulo
from weierstrass import weierstrass, normalize      # <-- ajustar nombre del módulo


def _preparar(largo, a, b, offset):
    """Repite los pasos previos del cifrador para un mensaje de `largo`
    caracteres. Devuelve (words, raw, w_min, w_max, rng_letters, letters)."""
    # `letters` se crea acá y no se importa: en el cifrador se baraja in situ.
    letters = [chr(i) for i in range(32, 256)]

    seed = make_seed(a, b, offset)
    rng_positions = HashRNG(seed + b"|positions")
    rng_letters = HashRNG(seed + b"|letters")
    rng_words = HashRNG(seed + b"|words")

    split_w = weierstrass(np.arange(1, largo + 2, dtype=float),
                          a, b, n_max=18, x_offset=offset)
    s_min, s_max = float(np.min(split_w)), float(np.max(split_w))
    words, i, k = [], 0, 0
    while i < largo:
        n = int(round(normalize(split_w[k], s_min, s_max, 3, 12)))
        words.append(list(range(i, min(i + n, largo))))   # índices en el mensaje
        i += n
        k += 1
    rng_words.shuffle(words)
    rng_letters.shuffle(letters)

    total_points = largo * 6 + len(words) + 10
    pool = list(range(3, total_points * 30 + 1, 3))
    n_pick = min(total_points, len(pool))
    for i in range(n_pick):
        j = rng_positions.randint(i, len(pool) - 1)
        pool[i], pool[j] = pool[j], pool[i]
    pool = pool[:n_pick]
    rng_positions.shuffle(pool)
    indices = np.array([float(p) + rng_positions.random() for p in pool])
    raw = weierstrass(indices, a, b, n_max=18, x_offset=offset)
    return words, raw, np.min(raw), np.max(raw), rng_letters, letters


def _intentar(cifrado, largo, a, b, offset):
    """Intenta parsear `cifrado` suponiendo un mensaje de `largo` caracteres.
    Devuelve la lista de fragmentos por palabra (en orden mezclado) o None."""
    try:
        words, raw, w_min, w_max, rng0, letters = _preparar(largo, a, b, offset)
        norm = lambda v, lo, hi: normalize(v, w_min, w_max, lo, hi)
        n = len(cifrado)

        def probar(p, c, rl, f):
            if c + 1 >= len(raw):
                return None
            na = int(round(norm(raw[c], 1, 5)))
            sa = int(round(norm(raw[c + 1], 1, 5)))
            total = f + na + sa
            if p + total > n:
                return None
            rl = copy.copy(rl)
            chars, previous = [None] * f, None
            for _ in range(na):
                letra = rl.choice(letters)
                while letra == previous:
                    letra = rl.choice(letters)
                chars.insert(rl.randint(0, len(chars)), letra)
                previous = letra
            previous = None
            for _ in range(sa):
                letra = rl.choice(letters)
                while letra == previous:
                    letra = rl.choice(letters)
                chars.append(letra)
                previous = letra
            seg = cifrado[p:p + total]
            if any(ch is not None and ch != real for ch, real in zip(chars, seg)):
                return None
            texto = "".join(r for ch, r in zip(chars, seg) if ch is None)
            return p + total, c + 2, rl, texto

        def empezar(j, p, c, rl):
            if j == len(words):
                return [] if p == n else None
            if c >= len(raw):
                return None
            wl = len(words[j])
            ancho = max(1, int(round(norm(raw[c], 1, max(1, wl // 2)))))
            return fragmentos(j, p, c + 1, rl, ancho, 0, [])

        def fragmentos(j, p, c, rl, ancho, acc, frags):
            wl = len(words[j])
            for f in range(min(ancho, wl - acc), 0, -1):
                r = probar(p, c, rl, f)
                if r is None:
                    continue
                res = fragmentos(j, r[0], r[1], r[2], ancho, acc + f, frags + [r[3]])
                if res is not None:
                    return res
            resto = empezar(j + 1, p, c, rl)       # la palabra termina acá
            return None if resto is None else [(ancho, frags)] + resto

        res = empezar(0, 0, 0, rng0)
        return None if res is None else (words, res)
    except (ZeroDivisionError, ValueError, OverflowError, IndexError):
        return None


def _armar(frags, ancho, wl):
    """Une los fragmentos de una palabra y repone los espacios descartados."""
    if not frags:
        return " " * wl
    d = wl - sum(len(f) for f in frags)
    seps = [0] * len(frags)
    for i in range(len(frags) - 1):          # línea corta => corte por espacio
        if len(frags[i]) < ancho and d > 0:
            seps[i] = 1
            d -= 1
    for i in range(len(frags) - 1):          # línea llena => ambiguo
        if len(frags[i]) == ancho and d > 0:
            seps[i] = 1
            d -= 1
    seps[-1] += max(d, 0)
    return "".join(f + " " * s for f, s in zip(frags, seps))


def descifrar(cifrado: str, a: float, b: int, offset: int) -> str:
    """Recupera el mensaje. El largo original no se guarda en el cifrado, así
    que se prueba cada largo posible hasta que todo el cifrado encaje."""
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))
    for largo in range(1, len(cifrado)):
        r = _intentar(cifrado, largo, a, b, offset)
        if r is None:
            continue
        words, partes = r
        trozos = [(w[0], _armar(frags, ancho, len(w)))
                  for w, (ancho, frags) in zip(words, partes)]
        trozos.sort()
        return "".join(t for _, t in trozos)
    raise ValueError("No se pudo descifrar: parámetros incorrectos o "
                     "cifrado alterado.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", required=True, help="texto cifrado (base64 por defecto)")
    ap.add_argument("--hex", action="store_true", help="el cifrado está en hexadecimal")
    ap.add_argument("-a", type=float, required=True)
    ap.add_argument("-b", type=int, required=True)
    ap.add_argument("-offset", "-o", type=int, required=True)
    args = ap.parse_args()

    datos = bytes.fromhex(args.c) if args.hex else base64.b64decode(args.c)
    print(descifrar(datos.decode("latin-1"), args.a, args.b, args.offset))