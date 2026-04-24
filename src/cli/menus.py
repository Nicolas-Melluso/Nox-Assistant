def menu_principal():
    print("Menú principal:")
    print("  1) OS Control")
    print("  2) Salir")
    try:
        return input("Opción principal > ").strip()
    except EOFError:
        return None

def menu_os_control():
    print("OS Control:")
    print("  1) Listar archivos")
    print("  2) Listar procesos")
    print("  3) Mostrar IP")
    print("  4) Volver")
    try:
        return input("Opción OS > ").strip()
    except EOFError:
        return None
