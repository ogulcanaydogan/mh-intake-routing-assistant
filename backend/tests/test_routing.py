from app import routing

def test_routing_minor():
    result = routing.route_user(5, 5, "under 18")
    assert result["bucket"].endswith("minor")
    assert "guardian" in result["recommendation"].lower()


def test_routing_high():
    result = routing.route_user(20, 5, "18+")
    assert result["bucket"] == "high"
    assert "unsafe" in result["recommendation"].lower()
