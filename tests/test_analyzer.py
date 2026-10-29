from src.analyzer import analyze


def test_russian_text():
    result = analyze("Привет, мир! Привет, Docker.")
    assert result["words"] == 4
    assert result["unique_words"] == 3
    assert result["sentences"] == 2
    assert result["top_words"][0] == {"word": "привет", "count": 2}
    assert result["longest_word"] == "Привет"


def test_blank_text():
    assert analyze("   ")["words"] == 0
    assert analyze("   ")["longest_word"] is None
    assert analyze("   ")["sentences"] == 0


def test_case_insensitive():
    result = analyze("Docker docker DOCKER")
    assert result["unique_words"] == 1
    assert result["top_words"] == [{"word": "docker", "count": 3}]
