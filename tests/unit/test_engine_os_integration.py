def test_engine_execute_open_youtube(engine):
    # La fixture `engine` usa MockIntentClassifier y SubprocessOSController(dry_run=True)
    r = engine.predict_intent("Abrir youtube")
    assert isinstance(r, dict)
    assert r.get("intent") in ("open", "open")
    action_res = engine.execute_skill(r)
    assert isinstance(action_res, dict)
    # Resultado esperado: ejecución dry_run True
    res = action_res.get("result") or {}
    assert action_res.get("success") is True or res.get("dry_run") is True
