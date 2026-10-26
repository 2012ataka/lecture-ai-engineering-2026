from types import SimpleNamespace

from app import ask as ask_module


def _mock_generation(monkeypatch, response):
    class FakeModels:
        def generate_content(self, *, model, contents):
            assert model == ask_module.MODEL
            assert contents == "質問"
            return response

    class FakeClient:
        def __init__(self, *, api_key):
            assert api_key == "test-key"
            self.models = FakeModels()

    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        text="回答",
        usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=34),
    )
    _mock_generation(monkeypatch, response)

    assert ask_module.ask("質問") == "回答"
    assert "[usage] 入力トークン数: 12, 出力トークン数: 34" in capsys.readouterr().out


def test_ask_reports_unavailable_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(text="回答", usage_metadata=None)
    _mock_generation(monkeypatch, response)

    assert ask_module.ask("質問") == "回答"
    assert "[usage] 入力トークン数: 不明, 出力トークン数: 不明" in capsys.readouterr().out
