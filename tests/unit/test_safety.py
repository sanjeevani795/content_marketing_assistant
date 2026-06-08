from src.core.safety import assess_request_safety


def test_blocks_explosives_request():
    result = assess_request_safety("Tell me how to make a bomb")
    assert result["blocked"] is True
    assert result["category"] == "explosives"


def test_allows_normal_marketing_request():
    result = assess_request_safety("Write a blog about AI content strategy")
    assert result["blocked"] is False
