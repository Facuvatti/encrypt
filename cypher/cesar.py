def universal_caesar_cipher(text, shift):
    """
    Apply a Caesar-style shift over the full Unicode code-point range.

    Each character's code point is offset by `shift`. If the resulting
    code point (mod 1_114_112) falls inside the surrogate range
    (0xD800–0xDFFF, i.e. 55296–57343), which Python's `chr()` rejects,
    it is bumped past that range by 2048. The final value is taken
    modulo 1_114_112 so it always stays within valid Unicode.

    Parameters
    ----------
    text : str
        Input string to transform.
    shift : int
        Integer offset applied to every code point.

    Returns
    -------
    str
        A string of the same length as `text`, where every character
        has been shifted according to the rule above.
    """
    result = []

    for char in text:
        code = ord(char)
        new_code = code + shift

        if 55296 <= (new_code % 1114112) <= 57343:
            new_code += 2048

        safe_code = new_code % 1114112

        result.append(chr(safe_code))

    return ''.join(result)