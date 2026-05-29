from src.agents.query_handler import handle_query


def test_chat_handler_smoke():
    result = handle_query("Write a linkedin post about AI content strategy")
    assert result["route"] == "linkedin"
