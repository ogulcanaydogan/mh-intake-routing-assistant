from app import safety, resources

def test_crisis_detection_english():
    assert safety.detect_crisis("I might commit suicide")
    assert safety.detect_crisis("I want to kill myself")


def test_crisis_detection_turkish():
    assert safety.detect_crisis("kendime zarar vermek istiyorum")
    assert safety.detect_crisis("intihar etmeyi düşünüyorum")


def test_crisis_response_includes_emergency():
    data = resources.load_resources("tr")
    result = safety.crisis_response(data)
    assert data["emergency_number"] in result
