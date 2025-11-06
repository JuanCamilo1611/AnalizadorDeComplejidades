def test_analyzer_module_importable():
    import importlib
    mod = importlib.import_module("src.analyzer.complexity")
    assert mod is not None