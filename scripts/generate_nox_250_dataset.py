from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CATALOG_PATH = RAW_DIR / "nox_250_intents_catalog.csv"
DATASET_PATH = RAW_DIR / "nox_250_intents_dataset.csv"


BASE_INTENT_SPECS = [
    ("pc_shutdown", "apaga la pc"),
    ("pc_restart", "reinicia la pc"),
    ("pc_sleep", "pon la pc en suspension"),
    ("pc_hibernate", "hiberna la pc"),
    ("pc_lock", "bloquea la pc"),
    ("set_volume", "pon el volumen al 70"),
    ("volume_up", "sube el volumen"),
    ("volume_down", "baja el volumen"),
    ("volume_mute", "silencia el volumen"),
    ("volume_unmute", "quita el silencio"),
    ("set_brightness", "pon el brillo al 60"),
    ("brightness_up", "sube el brillo"),
    ("brightness_down", "baja el brillo"),
    ("wifi_on", "activa el wifi"),
    ("wifi_off", "desactiva el wifi"),
    ("bluetooth_on", "activa el bluetooth"),
    ("bluetooth_off", "desactiva el bluetooth"),
    ("open_spotify", "abre spotify"),
    ("close_spotify", "cierra spotify"),
    ("open_discord", "abre discord"),
    ("close_discord", "cierra discord"),
    ("open_steam", "abre steam"),
    ("close_steam", "cierra steam"),
    ("open_chrome", "abre chrome"),
    ("close_chrome", "cierra chrome"),
    ("open_edge", "abre edge"),
    ("close_edge", "cierra edge"),
    ("open_youtube", "abre youtube"),
    ("close_youtube", "cierra youtube"),
    ("browser_search_web", "busca en la web"),
    ("browser_open_history", "abre el historial del navegador"),
    ("media_play", "reproduce"),
    ("media_pause", "pausa"),
    ("media_next_track", "siguiente cancion"),
    ("media_prev_track", "cancion anterior"),
    ("media_stop", "deten la reproduccion"),
    ("start_timer", "inicia un temporizador de 10 minutos"),
    ("stop_timer", "deten el temporizador"),
    ("set_alarm", "pon una alarma para las 7"),
    ("cancel_alarm", "cancela la alarma"),
    ("take_screenshot", "sacame una foto"),
    ("get_time", "que hora es"),
    ("get_date", "que fecha es hoy"),
    ("get_cpu_usage", "uso de cpu"),
    ("get_ram_usage", "uso de memoria"),
    ("get_battery_status", "estado de bateria"),
    ("get_network_status", "estado de la red"),
    ("open_task_manager", "abre el administrador de tareas"),
    ("mode_focus_on", "activa modo foco"),
    ("mode_gaming_on", "activa modo gaming"),
]

STYLES = ["standard", "gamer", "dev", "procrastinator", "quick"]


def style_command(base_command: str, style: str) -> str:
    if style == "standard":
        return base_command
    if style == "gamer":
        return f"nox {base_command} para la partida"
    if style == "dev":
        return f"nox {base_command} para codear"
    if style == "procrastinator":
        return f"che {base_command} que estoy procrastinando"
    return f"{base_command} ya"


def build_utterances(command: str, style: str) -> list[str]:
    if style == "gamer":
        prefixes = ["", "nox ", "bro ", "rapido "]
        suffixes = ["", " porfa", " ahora", " para rankear"]
    elif style == "dev":
        prefixes = ["", "nox ", "por favor ", "cuando puedas "]
        suffixes = ["", " para laburar", " en este sprint", " antes del deploy"]
    elif style == "procrastinator":
        prefixes = ["", "nox ", "porfa ", "dale "]
        suffixes = ["", " que me distraigo", " sin vueltas", " antes de perder tiempo"]
    elif style == "quick":
        prefixes = ["", "ya ", "nox ya ", "urgente "]
        suffixes = ["", " ahora", " rapido", " sin demora"]
    else:
        prefixes = ["", "nox ", "por favor ", "ahora "]
        suffixes = ["", " ahora", " por favor", " en este momento"]

    utterances: set[str] = set()
    for p in prefixes:
        for s in suffixes:
            utterances.add(f"{p}{command}{s}".strip())
            if len(utterances) >= 10:
                return sorted(utterances)
    return sorted(utterances)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if len(BASE_INTENT_SPECS) * len(STYLES) != 250:
        raise ValueError(
            "La combinacion base_intents x styles debe dar 250. "
            f"Actual: {len(BASE_INTENT_SPECS)} x {len(STYLES)} = {len(BASE_INTENT_SPECS) * len(STYLES)}"
        )

    catalog_rows = []
    dataset_rows = []

    for target_intent, command in BASE_INTENT_SPECS:
        for style in STYLES:
            alias_intent = f"{target_intent}__{style}"
            styled_command = style_command(command, style)
            catalog_rows.append(
                {
                    "intent": alias_intent,
                    "target_intent": target_intent,
                    "style": style,
                    "canonical_command": styled_command,
                }
            )
            for utt in build_utterances(styled_command, style):
                dataset_rows.append({"text": utt, "intent": alias_intent})

    catalog_df = pd.DataFrame(catalog_rows).drop_duplicates(subset=["intent"]).reset_index(drop=True)
    dataset_df = pd.DataFrame(dataset_rows).drop_duplicates(subset=["text", "intent"]).reset_index(drop=True)

    catalog_df.to_csv(CATALOG_PATH, index=False)
    dataset_df.to_csv(DATASET_PATH, index=False)

    print(f"Catalogo generado: {CATALOG_PATH}")
    print(f"Total intents: {catalog_df['intent'].nunique()}")
    print(f"Dataset generado: {DATASET_PATH}")
    print(f"Total ejemplos: {len(dataset_df)}")


if __name__ == "__main__":
    main()
