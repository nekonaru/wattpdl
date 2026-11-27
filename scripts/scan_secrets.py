"""Fail if staged files contain obvious credential patterns.

Local pre-commit hook (no external downloads): `python scripts/scan_secrets.py FILE...`.
Patterns are assembled so this scanner never flags its own source.
"""
import re
import sys

PATTERNS = [
    ("GitHub token", re.compile("gh" + "p_" + r"[A-Za-z0-9]{20,}")),
    ("GitHub OAuth token", re.compile("gho_" + r"[A-Za-z0-9]{20,}")),
    ("AWS key", re.compile("AKIA" + r"[0-9A-Z]{16}")),
    ("Private key", re.compile("BEGIN " + "PRIVATE KEY")),
    ("OpenSSH key", re.compile("BEGIN " + "OPENSSH PRIVATE KEY")),
]


def scan(paths):
    findings = []
    for name in paths:
        try:
            text = open(name, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for label, pattern in PATTERNS:
            if pattern.search(text):
                findings.append(f"{name}: {label}")
    return findings


def main():
    findings = scan(sys.argv[1:])
    if findings:
        print("Possible secrets found:")
        for line in findings:
            print("  " + line)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
