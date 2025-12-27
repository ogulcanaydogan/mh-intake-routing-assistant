from app import questionnaires

def test_phq9_scoring():
    answers = [0,1,2,3,0,1,2,3,0]
    assert questionnaires.score_questionnaire(answers) == sum(answers)


def test_gad7_scoring():
    answers = [3]*7
    assert questionnaires.score_questionnaire(answers) == 21


def test_bucket_logic():
    assert questionnaires.bucket_for_scores(3,3) == "low"
    assert questionnaires.bucket_for_scores(12,3) == "moderate"
    assert questionnaires.bucket_for_scores(3,16) == "high"
