"""
Test rapido del extractor de entidades. Corre desde la raiz del proyecto:
    python scripts/test_entities.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from entity_extractor import extract_entities

CASES = [
    # (frase, intent_esperado, entidades_esperadas)
    # Volumen / brillo
    ("pon el volumen al 70",          "volume_up",            {"value": 70}),
    ("volumen al 40",                 "set_volume",           {"value": 40}),
    ("sube el volumen a 50 por ciento","volume_up",            {"value": 50}),
    ("brillo al maximo",              "set_brightness",       {"value": 100}),
    ("baja el brillo al treinta",      "brightness_down",      {"value": 30}),
    # Timer
    ("pon un timer de diez minutos",  "start_timer",          {"duration_seconds": 600}),
    ("inicia un temporizador de 2 horas 30 minutos", "start_timer", {"duration_seconds": 9000}),
    ("timer de 45 segundos",          "start_timer",          {"duration_seconds": 45}),
    # Alarma
    ("pon una alarma a las 7",        "set_alarm",            {"time": "07:00"}),
    ("alarma a las 7:30",             "set_alarm",            {"time": "07:30"}),
    ("ponme una alarma a las siete",  "set_alarm",            {"time": "07:00"}),
    # Temperatura
    ("ajusta el termostato a 24 grados",   "thermostat_set_temp", {"temperature": 24}),
    ("pon el termostato a veinticuatro grados", "thermostat_set_temp", {"temperature": 24}),
    # Busqueda
    ("busca en la web noticias de python", "browser_search_web", {"query": "noticias de python"}),
    ("busca recetas de pasta",             "browser_search_web", {"query": "recetas de pasta"}),
    # Media seek
    ("adelanta diez segundos",         "media_seek_forward",  {"seconds": 10}),
    ("retrocede 30 segundos",          "media_seek_backward", {"seconds": 30}),
    # WhatsApp
    ("envia un mensaje a Juan diciendo llegas tarde", "send_whatsapp_message", {"contact": "Juan", "message": "llegas tarde"}),
    ("manda un whatsapp a Maria que diga hola", "send_whatsapp_message", {"contact": "Maria", "message": "hola"}),
    # Email
    ("envia un correo a Pedro con asunto reunion", "send_email", {"contact": "Pedro", "subject": "reunion"}),
    ("enviale un mail a anncomba@gmail.com que diga que la amo", "send_email", {"contact": "anncomba@gmail.com", "body": "que la amo"}),
    # YouTube query
    ("abri youtube un video de rocket league", "open_youtube", {"query": "rocket league"}),
    ("abri un video de rocket league", "open_youtube", {"query": "rocket league"}),
    ("abrime un video del rubius por favor", "open_youtube", {"query": "rubius"}),
    # Llamada
    ("llama a Carlos",                 "call_contact",        {"contact": "Carlos"}),
    # Archivos
    ("crea un archivo llamado notas",  "create_file",         {"filename": "notas"}),
    ("elimina el archivo llamado temp","delete_file",         {"filename": "temp"}),
    # Carpetas
    ("crea una carpeta llamada proyectos", "create_folder",   {"folder_name": "proyectos"}),
    # Clima
    ("dime el clima en Buenos Aires",  "get_weather",         {"city": "Buenos Aires"}),
    ("clima de Madrid",                "get_weather",         {"city": "Madrid"}),
    # Luces
    ("atenua las luces al 40",         "smart_lights_dim",    {"value": 40}),
    # Brillo con sinonimos
    ("subi el brillo al maximo",       "brightness_up",       {"value": 100}),
    ("baja el brillo al minimo",       "brightness_down",     {"value": 0}),
    # Foto vs screenshot
    ("sacame una foto",                "take_screenshot",     {"source": "camera"}),
    ("toma una captura de pantalla",   "take_screenshot",     {"source": "screen"}),
    # Sin entidades (no deben romper)
    ("apaga la pc",                    "pc_shutdown",         {}),
    ("abre spotify",                   "open_spotify",        {}),
]

passed = 0
failed = 0

for text, intent, expected in CASES:
    got = extract_entities(text, intent)
    ok = got == expected
    status = "OK" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
        print(f"[{status}] '{text}'")
        print(f"       intent:   {intent}")
        print(f"       esperado: {expected}")
        print(f"       obtenido: {got}")

print(f"\n{'='*50}")
print(f"Resultados: {passed}/{passed + failed} tests pasaron")
if failed == 0:
    print("Todos los tests pasaron!")
