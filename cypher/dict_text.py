def texto_a_diccionario(texto: str) -> dict:
    """Convierte un texto en {carácter: [posiciones de byte]} (latin-1)."""
    dic = {}
    for i, b in enumerate(texto.encode("latin-1")):
        dic.setdefault(chr(b), []).append(i)
    return dic