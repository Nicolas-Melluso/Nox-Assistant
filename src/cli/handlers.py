from types import SimpleNamespace
import os

def _cli_listar_archivos():
    try:
        files = os.listdir('.')
    except Exception:
        files = []
    print('Archivos (primeros 20):')
    for f in files[:20]:
        print(' -', f)

def _cli_listar_procesos():
    print('Listado de procesos: (stub)')

def _cli_mostrar_ip():
    print('IP actual: (stub)')

archivos = SimpleNamespace(cli_listar_archivos=_cli_listar_archivos)
procesos = SimpleNamespace(cli_listar_procesos=_cli_listar_procesos)
red = SimpleNamespace(cli_mostrar_ip=_cli_mostrar_ip)
