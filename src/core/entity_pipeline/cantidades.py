# Extracción de cantidades y unidades complejas
# Soporta expresiones como: "3 litros", "dos kilos", "media taza", "un cuarto de kilo", "1/2 litro", "cien gramos", "una docena de huevos"

import re
from typing import List, Dict, Any

# Lista de unidades soportadas (puedes expandirla)
UNIDADES = [
    "gramos", "gramo", "g", "kilos", "kilo", "kg", "litros", "litro", "l", "mililitros", "mililitro", "ml",
    "taza", "tazas", "docena", "docenas", "unidad", "unidades", "metro", "metros", "cm", "centimetro", "centimetros"
]

# Mapas para fracciones y palabras numéricas
FRACCIONES = {
    "media": 0.5,
    "un cuarto": 0.25,
    "un tercio": 1/3,
    "un medio": 0.5,
    "tercio": 1/3,
    "cuarto": 0.25,
    "tres cuartos": 0.75,
    "dos tercios": 2/3,
    "un octavo": 0.125,
    "octavo": 0.125
}
NUM_PALABRAS = {
    "uno": 1, "una": 1, "un": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "once": 11, "doce": 12, "cien": 100, "ciento": 100, "mil": 1000
}

# Regex para capturar cantidades complejas
REGEX_CANTIDAD = re.compile(r"""
    (?P<fraccion>(media|un\s+cuarto|un\s+tercio|un\s+medio|tercio|cuarto|tres\s+cuartos|dos\s+tercios|un\s+octavo|octavo))
    (\s+de)?\s+(?P<unidad>{unidades})
    |(?P<num_palabra>\b(?:uno|una|un|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|cien|ciento|mil)\b)\s+(?P<unidad2>{unidades})
    |(?P<fraccion_num>\d+/\d+)\s+(?P<unidad3>{unidades})
    |(?P<num>\d+[\.,]?\d*)\s+(?P<unidad4>{unidades})
""".format(unidades="|".join(UNIDADES)), re.IGNORECASE | re.VERBOSE)

def extraer_cantidades(texto: str) -> List[Dict[str, Any]]:
    """Extrae cantidades y unidades complejas del texto."""
    resultados = []
    for match in REGEX_CANTIDAD.finditer(texto):
        cantidad = None
        unidad = None
        if match.group("fraccion"):
            cantidad = FRACCIONES.get(match.group("fraccion").lower(), None)
            unidad = match.group("unidad")
        elif match.group("num_palabra"):
            cantidad = NUM_PALABRAS.get(match.group("num_palabra").lower(), None)
            unidad = match.group("unidad2")
        elif match.group("fraccion_num"):
            num, den = match.group("fraccion_num").split("/")
            cantidad = float(num) / float(den)
            unidad = match.group("unidad3")
        elif match.group("num"):
            cantidad = float(match.group("num").replace(",", "."))
            unidad = match.group("unidad4")
        # Ajuste para docena/docenas
        if cantidad is not None and unidad is not None:
            unidad_l = unidad.lower()
            if unidad_l in ["docena", "docenas"]:
                cantidad = cantidad * 12
            elif unidad_l in ["media docena"]:
                cantidad = cantidad * 6
            resultados.append({
                "cantidad": cantidad,
                "unidad": unidad_l,
                "texto": match.group(0)
            })
    return resultados

# Ejemplo de uso
if __name__ == "__main__":
    ejemplos = [
        "media taza de leche",
        "un cuarto de kilo de pan",
        "tres cuartos de litro",
        "dos kilos de manzanas",
        "1/2 litro de agua",
        "cien gramos de queso",
        "una docena de huevos",
        "3 litros de jugo",
        "250 ml de aceite"
    ]
    for ej in ejemplos:
        print(ej, "->", extraer_cantidades(ej))
