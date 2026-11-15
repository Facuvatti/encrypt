def cifrar_rot256(texto: str, clave: int) -> tuple[str, str]:
  """Cifra un texto usando ROT256 y devuelve una tupla con:

  1. El texto cifrado.
  2. El carácter que reemplaza al espacio (' ').
  """
  datos = texto.encode("latin-1")
  cifrados = bytes((b + clave) % 256 for b in datos)
  texto_cifrado = cifrados.decode("latin-1")

  # Calcular qué carácter reemplaza al espacio (código 32)
  nuevo_codigo_espacio = (32 + clave) % 256

  return texto_cifrado
def descifrar_rot256(texto_cifrado: str, clave: int) -> str:
  """Descifra un texto previamente cifrado con ROT256."""
  datos = texto_cifrado.encode("latin-1")
  descifrados = bytes((b - clave) % 256 for b in datos)
  return descifrados.decode("latin-1")

