def test_parser_module_importable():
    import importlib
    mod = importlib.import_module("src.parser.parser")
    assert hasattr(mod, "parse_code")