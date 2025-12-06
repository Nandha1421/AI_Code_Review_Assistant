import shutil
import subprocess
from typing import List

from app.schema import Issue, Severity


def run_flake8(path: str) -> List[Issue]:
    if not shutil.which("flake8"):
        return []

    try:
        res = subprocess.run(["flake8", path], capture_output=True, text=True, check=False)
        out = res.stdout.strip()
        issues = []
        if not out:
            return issues

        for line in out.splitlines():
            # expected: file:line:col: CODE message
            parts = line.split(":", 3)
            if len(parts) >= 4:
                _, line_no, col, rest = parts
                code_and_msg = rest.strip()
                code = code_and_msg.split()[0]
                msg = " ".join(code_and_msg.split()[1:])
                issues.append(
                    Issue(
                        id=f"F-{code}",
                        rule=code,
                        message=msg,
                        severity=Severity.MEDIUM,
                        line_start=int(line_no),
                        line_end=int(line_no),
                    )
                )
        return issues
    except Exception:
        return []
