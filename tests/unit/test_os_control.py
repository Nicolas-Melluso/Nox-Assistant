from src.core.os_control import SubprocessOSController


def test_subprocess_oscontroller_dry_run():
    c = SubprocessOSController(dry_run=True)
    r = c.run_command("echo hola", shell=True)
    assert r.get("ok") is True and r.get("dry_run") is True
    r2 = c.start_app("spotify")
    assert r2.get("ok") is True and r2.get("dry_run") is True
    r3 = c.open_path("http://example.com")
    assert r3.get("ok") is True and r3.get("dry_run") is True
