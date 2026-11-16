# generar_corpus.py
import random
import time
from encriptar import cypher as cifrar

# --- Reproducibilidad (importante para volver a correr las pruebas) ---
random.seed(12345)

# --- Banco de palabras: español realista ---
# Usá palabras reales para que el test refleje tu caso de uso.
# Si querés más realismo todavía, leé un .txt y cortá trozos random.
PALABRAS = """el la de que y a en un ser se no haber por con su para como estar
tener le lo todo pero mas hacer o poder decir este ir otro ese si me ya ver
porque dar cuando muy sin vez mucha saber tiempo mismo ahora cada vida otro
despues te otros aunque esa eso hombre antes alguno gran cosa poco lengua
mental hecho siempre tanto gente entonces decir junto aquel pasar tambien
hasta desde donde durante nuevo mundo casa pais trabajo noche dia agua fuego
tierra aire luz sombra color sonido palabra numero forma punto linea curva
circulo cuadrado triangulo esfera cubo espacio materia energia fuerza
movimiento cambio causa efecto principio final verdad mentira amor odio miedo
valor honor justicia libertad igualdad fraternidad""".split()

def texto_aleatorio(min_palabras=5, max_palabras=300):
    n = random.randint(min_palabras, max_palabras)
    return " ".join(random.choice(PALABRAS) for _ in range(n))

def params_aleatorios():
    a      = random.uniform(0.001, 4.0)
    b      = random.randint(2, 1_000_000)       # moderado: evita OverflowError
    offset = random.randrange(1, 100_001, 100)  # 1, 101, 201, ...
    return a, b, offset

# --- Loop principal ---
OBJETIVO_BYTES = 20 * 1024 * 1024   # 20 MB
PATH = "salida2.bin"

with open(PATH, "wb") as f:
    total = 0
    i = 0
    t0 = time.time()
    while total < OBJETIVO_BYTES:
        texto = texto_aleatorio()
        a, b, offset = params_aleatorios()
        _, result_bytes = cifrar(texto, a, b, offset)
        f.write(result_bytes)
        total += len(result_bytes)
        i += 1
        if i % 100 == 0:
            print(f"{i} cifrados | {total/1e6:.2f} MB | {time.time()-t0:.1f}s")

print(f"Listo: {i} cifrados, {total/1e6:.2f} MB en {PATH}")