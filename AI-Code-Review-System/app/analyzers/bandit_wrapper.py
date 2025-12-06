import shutil
import subprocess
import json
from typing import List

from app.schema import Issue, Severity


def run_bandit(path: str) -> List[Issue]:
    """Run bandit on the file path and return normalized Issue objects.
    If bandit is not installed, return an empty list."""
    if not shutil.which("bandit"):
        return []

    try:
        res = subprocess.run(["bandit", "-f", "json", "-r", path], capture_output=True, text=True, check=False)
        out = res.stdout.strip()
        if not out:
            return []
        data = json.loads(out)
        issues = []
        for item in data.get("results", []):
            lineno = item.get("line_number")
            test_id = item.get("test_id")
            text = item.get("issue_text")
            severity = item.get("issue_severity", "MEDIUM").upper()
            sev = Severity.MEDIUM
            if severity == "HIGH":
                sev = Severity.HIGH
            elif severity == "LOW":
                sev = Severity.LOW
            elif severity == "MEDIUM":
                sev = Severity.MEDIUM
            issues.append(
                Issue(
                    id=f"B-{test_id}",
                    rule=test_id,
                    message=text,
                    severity=sev,
                    line_start=lineno,
                    line_end=lineno,
                )
            )
        return issues
    except Exception:
        return []
