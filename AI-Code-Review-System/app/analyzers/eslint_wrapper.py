import shutil
import subprocess
import json
from typing import List

from app.schema import Issue, Severity


def run_eslint(path: str) -> List[Issue]:
    """Run eslint (via npx if available) and return normalized Issue objects.
    If eslint is not available, return an empty list."""
    # prefer npx so local node/npm users don't need global eslint
    cmd = None
    if shutil.which("npx"):
        cmd = ["npx", "eslint", "-f", "json", path]
    elif shutil.which("eslint"):
        cmd = ["eslint", "-f", "json", path]
    else:
        return []

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        out = res.stdout.strip()
        if not out:
            return []
        data = json.loads(out)
        issues: List[Issue] = []
        # eslint returns a list per-file
        for file_res in data:
            for msg in file_res.get("messages", []):
                rule = msg.get("ruleId") or "eslint"
                severity_num = msg.get("severity", 2)
                severity = Severity.MEDIUM
                if severity_num == 2:
                    severity = Severity.HIGH
                elif severity_num == 1:
                    severity = Severity.MEDIUM
                issues.append(
                    Issue(
                        id=f"ES-{rule}",
                        rule=rule,
                        message=msg.get("message", ""),
                        severity=severity,
                        line_start=msg.get("line"),
                        line_end=msg.get("endLine", msg.get("line")),
                    )
                )
        return issues
    except Exception:
        return []
