import numpy as np
import matplotlib.pyplot as plt

def weierstrass(x, a=0.5, b=3, n_max=100, x_offset=0, y_offset=0):
    if not isinstance(b,int): 
        return "Debe ser entero"
    if x_offset % 100 == 0 and x_offset != 0:
        return "No puede ser multiplo de 100"
    # Aplicamos el offset horizontal directamente a la x antes del cálculo
    x_shifted = x - x_offset 
    
    y = np.zeros_like(x_shifted,dtype=float)
    for n in range(n_max):
        y += (a**n) * np.cos(((b*np.pi)**n) * np.pi * x_shifted)
        
    # Aplicamos el offset vertical al resultado final
    return y + y_offset
def normalize_range(y, desired_min, desired_max):
    # 1. Encontrar los extremos actuales de la función
    current_min = np.min(y)
    current_max = np.max(y)
    
    # 2. Transformación lineal al nuevo rango
    normalized_y = desired_min + ((y - current_min) / (current_max - current_min)) * (desired_max - desired_min)
    return normalized_y

def weierstrass_normalized(x, a=0.5, b=3, n_max=100, x_offset=0, y_offset=0,min=0,max=1):
    y = weierstrass(x, a, b, n_max, x_offset, y_offset)
    return normalize_range(y,min,max)