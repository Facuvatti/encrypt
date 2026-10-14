import numpy as np
import matplotlib.pyplot as plt

def weierstrass(x, a=0.5, b=3, n_max=50):
    y = np.zeros_like(x)
    for n in range(n_max):
        y += (a**n) * np.cos((b**n) * np.pi * x)
    return y

def normalizar_rango(y, min_deseado, max_deseado):
    # 1. Encontrar los extremos actuales de la función
    min_actual = np.min(y)
    max_actual = np.max(y)
    
    # 2. Transformación lineal al nuevo rango
    y_normalizada = min_deseado + ((y - min_actual) / (max_actual - min_actual)) * (max_deseado - min_deseado)
    return y_normalizada

# 1. Definir el dominio x
x = np.linspace(-2, 2, 10000)

# 2. Calcular la función de Weierstrass original
y_original = weierstrass(x, a=0.5, b=3)

# 3. Definir tus límites deseados para "Y"
MIN_Y = 1
MAX_Y = 10

# 4. Normalizar la función
y_normalizada = normalizar_rango(y_original, MIN_Y, MAX_Y)

# --- Verificación en consola ---
print(f"Rango original de Y: [{y_original.min():.4f}, {y_original.max():.4f}]")
print(f"Rango normalizado de Y: [{y_normalizada.min():.4f}, {y_normalizada.max():.4f}]")

# --- Graficar el resultado con plt ---
plt.figure(figsize=(10, 5))
plt.plot(x, y_normalizada, color='darkviolet', lw=0.8, label='Weierstrass Normalizada')

# Líneas horizontales de guía para ver los límites reales en Y
plt.axhline(y=MAX_Y, color='red', linestyle='--', alpha=0.5, label=f'Máximo deseado ({MAX_Y})')
plt.axhline(y=MIN_Y, color='green', linestyle='--', alpha=0.5, label=f'Mínimo deseado ({MIN_Y})')

plt.title(f'Función de Weierstrass acotada exactamente entre {MIN_Y} y {MAX_Y}')
plt.xlabel('Eje X')
plt.ylabel('Eje Y (Normalizado)')
plt.grid(True, alpha=0.3)
plt.legend(loc='upper right')
plt.show()
