import textwrap
import random
import numpy as np
from weierstrass import weierstrass, normalize
import argparse
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'ñ', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
def randint(min, max, divider):
    # 1. Count how many valid numbers (NOT multiples) exist in the range
    total_valid = (max - min + 1) - (max // divider - (min - 1) // divider)
    
    # 2. Pick a random index and mathematically map it to the actual valid number
    return min + (k := random.randrange(total_valid)) + (k + min - 1) // (divider - 1)
example = "Hay mañanas en las que el mundo parece detenerse un instante antes de que el reloj marque la prisa. El café humea sobre la mesa de madera vieja, la luz de la ventana dibuja figuras geométricas en el suelo y el silencio no es un vacío, sino una forma de compañía. Vivimos atrapados en la dictadura de los calendarios, corriendo detrás de metas que cambian de forma justo cuando creemos alcanzarlas, como si la vida fuera una lista interminable de casillas por marcar. Sin embargo, si uno se detiene a mirar con calma, descubre que lo importante rara vez hace ruido."
parser = argparse.ArgumentParser(description='encripytion')
parser.add_argument("-text","-t", type=str, help="text to encrypt inside of quotes",default=example)
parser.add_argument("-a", type=float, default=random.uniform(0,2))
parser.add_argument("-b", type=int, help="b must be an integer",default=random.randint(2,10))
parser.add_argument("-offset","-o", type=int, help="offset must be an integer not multiple of 100 and different than 0", default=randint(1,1000,100))
args = parser.parse_args()
text = args.text
words = text.split(" ")
# print(words)
indices = np.arange(len(words))
x = np.linspace(0, 3000, 10) if len(words) < 3000 else indices
raw_weierstrass = weierstrass(indices, args.a, args.b, x_offset=args.offset)
w_min = np.min(raw_weierstrass)
w_max = np.max(raw_weierstrass)
for i, word in enumerate(words):
    syllables = [] 
    half = len(word) // 2
    val = raw_weierstrass[i]
    normalized = normalize(val,w_min,w_max,1,half-1)
    rounded = int(round(normalized))
    words[i] = textwrap.wrap(word,width=max(1,rounded))
print(words)
for i, word in enumerate(words):
    for j, syl in enumerate(word):
        val = raw_weierstrass[i*j]
        normalized = normalize(val,w_min,w_max,1,5)
        length = int(round(normalized))
        for k in range(0,length):
            val = raw_weierstrass[j*k+i]
            letter_index = int(round(normalize(val,w_min,w_max,0,26)))
            letter = letters[letter_index]
            word[j] = letter + word[j]
print(words)
# with open("output.txt", "w") as f:
#     f.write()