from lexico import *
import sys
from sintactico import *
def main():
    print("CompiladorCito")

    if len(sys.argv) != 2:  
        sys.exit("Error: Se necesita un archivo para compilar")
    with open(sys.argv[1], 'r') as archivo:
        fuente = archivo.read()

#codigo = '== > <= + < * - / => != 12 12.8 5 "String" "Ejemplo" IF var = 0'

    lexico = Lexico(fuente)             #analisis lexico
    sintactico = Sintactico(lexico)     #analisis sintactico     

    sintactico.programa()               #Empieza al analizador sintactico
    print("Analisis completado")

main()
