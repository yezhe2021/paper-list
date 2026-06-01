from __future__ import annotations

import datetime as dt
import subprocess
import sys
from pathlib import Path


LOG_PATH = Path("latest_run.log")


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    with LOG_PATH.open("a", encoding="utf-8") as log:
        log.write(f"$ {' '.join(command)}\n")
        log.write(result.stdout)
        if result.stdout and not result.stdout.endswith("\n"):
            log.write("\n")
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(command)}")
    return result


def has_report_changes() -> bool:
    result = run(["git", "status", "--short", "reports"], check=False)
    return bool(result.stdout.strip())


def main() -> int:
    LOG_PATH.write_text(f"Weekly update started: {dt.datetime.now().isoformat()}\n", encoding="utf-8")

    run([sys.executable, "paper_finder.py"])
    run([sys.executable, "query_related_papers.py"])

    if not has_report_changes():
        print("No report changes to publish.")
        return 0

    run(["git", "add", "reports"])
    commit_message = f"Update paper reports {dt.date.today().isoformat()}"
    commit = run(["git", "commit", "-m", commit_message], check=False)
    if commit.returncode != 0 and "nothing to commit" not in commit.stdout.lower():
        raise RuntimeError("git commit failed")
    if commit.returncode == 0:
        run(["git", "push"])
        print("Reports updated and pushed.")
    else:
        print("No commit created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
