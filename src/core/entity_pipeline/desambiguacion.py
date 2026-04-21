
# --- Desambiguación contextual mejorada ---
import re

COLORES = ["rojo", "azul", "verde", "amarillo", "blanco", "negro", "naranja", "violeta", "morado", "rosa"]
DISPOSITIVOS_MODO = ["ventilador", "luz", "alarma", "musica", "televisor"]
ACCIONES_PUERTA = ["abrir", "cerrar", "abrime", "cerrame"]
ACCIONES_VOLUMEN = ["sube", "baja", "aumenta", "disminuye"]
ACCIONES_ALARMA = ["poner", "quitar", "activa", "desactiva", "configura"]


# Busca color después de 'en' o 'a' (ej: 'luz en azul', 'luz a rojo')
def es_color_en_contexto(text):
    for color in COLORES:
        # Busca color después de 'en' o 'a'
        if re.search(rf"(en|a) {color}\b", text):
            return color
        # Busca color en la frase
        if re.search(rf"\\b{color}\\b", text):
            return color
    return None

def hay_accion(text, acciones):
    return any(re.search(rf"\\b{accion}\\b", text) for accion in acciones)


def desambiguar_entidades_por_contexto(entities, text):
    """
    Aplica reglas contextuales para desambiguar entidades.
    - Extrae color en frases como 'pone la luz roja'.
    - Evita duplicados de entidades MODO/MODO_TIPO.
    """
    text_lower = text.lower()
    nuevas_entidades = []
    hay_modo = any(e["text"].lower() == "modo" for e in entities)
    colores_extraidos = set()
    modo_tipos_extraidos = set()
    for ent in entities:
        ent_text = ent["text"].lower()
        ent_label = ent["label"]

        # Regla: Si hay "modo" y un dispositivo ambiguo, priorizar como MODO
        if ent_label == "DISPOSITIVO" and ent_text in DISPOSITIVOS_MODO and hay_modo:
            ent = ent.copy()
            ent["label"] = "MODO"

        # Regla: "puerta" solo es DISPOSITIVO si hay acción relevante
        if ent_text == "puerta":
            if hay_accion(text_lower, ACCIONES_PUERTA):
                ent = ent.copy()
                ent["label"] = "DISPOSITIVO"

        # Regla: Si "luz" y hay color, agregar entidad COLOR (también en frases como 'pone la luz roja')
        if ent_text == "luz":
            # Busca color después de 'luz' (ej: 'luz roja')
            match = re.search(r"luz (\w+)", text_lower)
            if match and match.group(1) in COLORES:
                color = match.group(1)
                if color not in colores_extraidos:
                    nuevas_entidades.append({"text": color, "label": "COLOR"})
                    colores_extraidos.add(color)
            else:
                color = es_color_en_contexto(text_lower)
                if color and color not in colores_extraidos:
                    nuevas_entidades.append({"text": color, "label": "COLOR"})
                    colores_extraidos.add(color)

        # Regla: "volumen" es DISPOSITIVO solo si hay acción relevante
        if ent_text == "volumen":
            if hay_accion(text_lower, ACCIONES_VOLUMEN):
                ent = ent.copy()
                ent["label"] = "DISPOSITIVO"

        # Regla: "alarma" es DISPOSITIVO solo si hay acción relevante
        if ent_text == "alarma":
            if hay_accion(text_lower, ACCIONES_ALARMA):
                ent = ent.copy()
                ent["label"] = "DISPOSITIVO"

        # Regla avanzada: "modo noche", "modo ahorro", etc. Evita duplicados
        if ent_text == "modo":
            match = re.search(r"modo (\w+)", text_lower)
            if match:
                modo_tipo = match.group(1)
                if modo_tipo not in modo_tipos_extraidos:
                    nuevas_entidades.append({"text": modo_tipo, "label": "MODO_TIPO"})
                    modo_tipos_extraidos.add(modo_tipo)

        # Evita duplicados exactos
        if not any(e["text"] == ent["text"] and e["label"] == ent["label"] for e in nuevas_entidades):
            nuevas_entidades.append(ent)
    return nuevas_entidades
