import re
from typing import List
from app.schema import Issue, Severity


def run_heuristics(code: str, language: str = "python") -> List[Issue]:
    issues: List[Issue] = []

    # Detect use of eval/exec
    if re.search(r"\beval\b|\bexec\b", code):
        issues.append(
            Issue(
                id="H-EVAL",
                rule="eval-exec-usage",
                message="Use of eval/exec detected; can lead to code injection.",
                severity=Severity.CRITICAL,
            )
        )

    # Hardcoded secrets (very simple regex)
    if re.search(r"(?i)api[_-]?key\s*[=:]\s*['\"]?[A-Za-z0-9-_]{20,}['\"]?", code):
        issues.append(
            Issue(
                id="H-SECRET",
                rule="hardcoded-secret",
                message="Possible hardcoded API key or secret detected.",
                severity=Severity.HIGH,
            )
        )

    # Missing try/except around common IO or network calls - heuristic: 'open(' or 'requests.' without 'try'
    if "open(" in code and "try:" not in code:
        issues.append(
            Issue(
                id="H-TRY-OPEN",
                rule="missing-try-open",
                message="File I/O detected without try/except for error handling.",
                severity=Severity.MEDIUM,
            )
        )

    if "requests." in code and "try:" not in code:
        issues.append(
            Issue(
                id="H-TRY-REQ",
                rule="missing-try-requests",
                message="Network calls detected without error handling.",
                severity=Severity.MEDIUM,
            )
        )

    # Inefficient loop pattern: nested loops over list indexing (very naive)
    if re.search(r"for\s+\w+\s+in\s+\w+:\s*\n\s*for\s+\w+\s+in\s+\w+:", code):
        issues.append(
            Issue(
                id="H-NESTED-LOOP",
                rule="nested-loop-inefficient",
                message="Nested loops detected — verify complexity and large inputs.",
                severity=Severity.MEDIUM,
            )
        )

    return issues
