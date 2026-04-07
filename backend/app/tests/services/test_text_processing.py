from app.utils.text_processing import preprocess_for_indexing


def test_preprocess_for_indexing_normalizes_and_removes_stopwords():
    payload = preprocess_for_indexing("A Resolução, de 2026, é para o IFES!!!")

    assert payload["normalized_text"] == "a resolucao de 2026 e para o ifes"
    assert payload["raw_tokens"] == ["a", "resolucao", "de", "2026", "e", "para", "o", "ifes"]
    assert payload["tokens"] == ["resolucao", "2026", "ifes"]
    assert payload["processed_text"] == "resolucao 2026 ifes"
    assert payload["positions_by_term"] == {
        "resolucao": [0],
        "2026": [1],
        "ifes": [2],
    }
    assert payload["term_count"] == 3
    assert payload["token_count"] == 3
