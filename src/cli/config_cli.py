def run_feature_flags_ui(flags_obj):
    """Interfaz CLI simplificada para alternar feature flags.
    flags_obj debe exponer `list_flags()` y `set_flag(interface, category, name, value)`.
    """
    try:
        flags = flags_obj.list_flags()
    except Exception:
        print("No se pudieron cargar los feature flags.")
        return
    print("Feature flags (modo CLI simplificado). Escribe 'salir' para salir.")
    while True:
        interfaces = list(flags.keys())
        for i, name in enumerate(interfaces, start=1):
            print(f"{i}) {name}")
        choice = input("Interfaz (número o 'salir') > ").strip()
        if choice.lower() in ('salir', 'exit', 'q'):
            break
        if not choice.isdigit():
            print("Opción no válida.")
            continue
        idx = int(choice) - 1
        if idx < 0 or idx >= len(interfaces):
            print("Opción no válida.")
            continue
        interfaz = interfaces[idx]
        categorias = list(flags[interfaz].keys())
        for j, c in enumerate(categorias, start=1):
            print(f"{j}) {c}")
        cchoice = input("Categoría (número) > ").strip()
        if not cchoice.isdigit():
            continue
        cidx = int(cchoice) - 1
        if cidx < 0 or cidx >= len(categorias):
            continue
        categoria = categorias[cidx]
        feats = flags[interfaz][categoria]
        if not isinstance(feats, dict):
            print("No hay features booleanos en esta categoría.")
            continue
        feature_keys = [k for k, v in feats.items() if isinstance(v, bool)]
        for k in feature_keys:
            print(f"- {k}: {feats[k]}")
        fname = input("Feature para alternar (nombre) > ").strip()
        if fname not in feats:
            print("Feature no encontrada.")
            continue
        nuevo = not feats[fname]
        flags_obj.set_flag(interfaz, categoria, fname, nuevo)
        print(f"{'Habilitado' if nuevo else 'Deshabilitado'}: {interfaz} / {categoria} / {fname}")
