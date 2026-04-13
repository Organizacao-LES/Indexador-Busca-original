from collections import namedtuple
from datetime import datetime

from app.strategies.search_ranking_strategy import SearchRankingStrategy


Row = namedtuple(
    "Row",
    [
        "document_id",
        "title",
        "document_date",
        "term",
        "idf",
        "tf",
        "posicao_inicial",
    ],
)


def test_ranking_strategy_prioritizes_coverage_and_position():
    strategy = SearchRankingStrategy()
    rows = [
        Row(1, "Portaria IFES", datetime.utcnow(), "ifes", 1000, 1, 40),
        Row(2, "Relatório de Pesquisa IFES", datetime.utcnow(), "ifes", 1000, 1, 0),
        Row(2, "Relatório de Pesquisa IFES", datetime.utcnow(), "pesquisa", 1000, 1, 2),
    ]

    ranked = strategy.rank(rows, ["ifes", "pesquisa"])

    assert ranked[0]["document_id"] == 2
    assert ranked[0]["score"] > ranked[1]["score"]
