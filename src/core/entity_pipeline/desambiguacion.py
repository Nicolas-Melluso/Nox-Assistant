def desambiguar_entidades_por_contexto(entities, text):
    text_lower = text.lower()
    nuevas_entidades = []
    colores = ["rojo", "azul", "verde", "amarillo", "blanco", "negro", "naranja", "violeta", "morado", "rosa"]
    dispositivos_modo = ["ventilador", "luz", "alarma", "musica", "televisor"]
    hay_modo = any(e["text"].lower() == "modo" for e in entities)
    for ent in entities:
        if ent["label"] == "DISPOSITIVO" and ent["text"].lower() in dispositivos_modo and hay_modo:
            ent = ent.copy()
            ent["label"] = "MODO"
        if ent["text"].lower() == "puerta":
            if any(accion in text_lower for accion in ["abrir", "cerrar"]):
                ent = ent.copy()
                ent["label"] = "DISPOSITIVO"
        if ent["text"].lower() == "luz":
            for color in colores:
                if color in text_lower:
                    nuevas_entidades.append({"text": color, "label": "COLOR"})
        if ent["text"].lower() == "volumen":
            if any(accion in text_lower for accion in ["sube", "baja", "aumenta", "disminuye"]):
                ent = ent.copy()
                ent["label"] = "DISPOSITIVO"
        if ent["text"].lower() == "alarma":
            if any(accion in text_lower for accion in ["poner", "quitar", "activa", "desactiva"]):
                ent = ent.copy()
                ent["label"] = "DISPOSITIVO"
        nuevas_entidades.append(ent)
    return nuevas_entidades
