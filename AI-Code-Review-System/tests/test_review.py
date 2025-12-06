from app.review import review_code
from app.schema import ReviewRequest


def test_eval_detection():
    code = "x = eval('1+1')\nprint(x)"
    req = ReviewRequest(code=code, language="python")
    res = review_code(req)
    # Heuristic should detect eval usage and create an issue with id H-EVAL
    assert any(issue.id == "H-EVAL" for issue in res.issues)
