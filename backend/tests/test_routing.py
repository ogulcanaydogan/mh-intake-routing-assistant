from app import routing

def test_routing_minor():
    result = routing.route_user(5, 5, "under 18")
    assert result["bucket"].endswith("minor")
    assert "guardian" in result["recommendation"].lower()


def test_routing_high():
    result = routing.route_user(20, 5, "18+")
    assert result["bucket"] == "high"
    assert "unsafe" in result["recommendation"].lower()


def test_routing_explanation_contains_thresholds():
    result = routing.route_user(12, 5, "18+")
    assert "explanation" in result
    phq9_comparisons = result["explanation"]["phq9"]["comparisons"]
    assert any(c["threshold"] == "moderate" and c["met"] for c in phq9_comparisons)
    decision = result["explanation"]["decision"]
    assert decision["selected_bucket"].startswith("moderate")
    assert decision["basis"] in {"phq9", "gad7"}
