import tempfile
import os
from typing import List

from app.schema import ReviewRequest, ReviewResponse, Issue, Severity

from app.heuristics import run_heuristics
from app.llm_agent import augment_issues_with_suggestions

try:
    from app.analyzers.flake8_wrapper import run_flake8
except Exception:
    def run_flake8(path: str):
        return []

try:
    from app.analyzers.bandit_wrapper import run_bandit
except Exception:
    def run_bandit(path: str):
        return []


def review_code(request: ReviewRequest) -> ReviewResponse:
    code = request.code
    language = (request.language or "python").lower()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=(".py" if language == "python" else ".js"))
    try:
        tmp.write(code.encode("utf-8"))
        tmp.flush()
        tmp.close()

        issues: List[Issue] = []

        # Run language-specific analyzers
        if language == "python":
            issues += run_flake8(tmp.name)
            issues += run_bandit(tmp.name)
        elif language == "javascript":
            try:
                from app.analyzers.eslint_wrapper import run_eslint

                issues += run_eslint(tmp.name)
            except Exception:
                pass

        # Run heuristics
        issues += run_heuristics(code, language)

        # Augment with LLM-like suggestions (RAG + GPT-2 agent)
        issues = augment_issues_with_suggestions(issues, code, language)

        summary = f"Found {len(issues)} issue(s)."
        return ReviewResponse(issues=issues, summary=summary)
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
