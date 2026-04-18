"""
Test rapido para la capa de correccion de intent.
Corre desde la raiz del proyecto:
    python scripts/test_intent_router.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from intent_router import route_intent

CASES = [
    ("Abri youtube un video de rocket league", "close_youtube", "open_youtube"),
    ("Abrime un video del rubius por favor", "set_alarm", "open_youtube"),
    ("Cerrame youtube", "open_youtube", "close_youtube"),
    ("Sacame una foto", "set_alarm", "take_screenshot"),
    ("Enviale un mail a anncomba@gmail.com", "send_whatsapp_message", "send_email"),
    ("Subi el brillo al maximo", "brightness_up", "set_brightness"),
    ("Volumen al 40", "call_contact", "set_volume"),
    ("Brillo al 25", "set_alarm", "set_brightness"),
    ("pon el volumen al 70", "volume_down__dev", "set_volume"),
]

passed = 0
failed = 0

for text, predicted, expected in CASES:
    got, reason = route_intent(text, predicted)
    ok = got == expected
    if ok:
        passed += 1
    else:
        failed += 1
        print(f"[FAIL] text={text}")
        print(f"       predicted={predicted}")
        print(f"       expected={expected}")
        print(f"       got={got}")
        print(f"       reason={reason}")

print(f"\nResultados: {passed}/{passed + failed} tests pasaron")
if failed == 0:
    print("Todos los tests pasaron!")
