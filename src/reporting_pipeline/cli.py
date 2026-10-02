from __future__ import annotations

import json
import sys

from .core import parse_csv, serialise_sample


def smoke() -> int:
    print(json.dumps(serialise_sample(), indent=2, sort_keys=True))
    return 0


def reverse_test() -> int:
    cases: list[dict[str, str]] = []
    corruptions = [
        ("schema-drift", "record_id,period,entity,total\nR1,2026-09,A,10\n"),
        ("duplicate-id", "record_id,period,entity,amount\nR1,2026-09,A,10\nR1,2026-09,B,20\n"),
    ]
    for name, payload in corruptions:
        try:
            parse_csv(payload)
        except ValueError as exc:
            cases.append({"case": name, "status": "PASS", "error": str(exc)})
        else:
            cases.append({"case": name, "status": "FAIL", "error": "corruption accepted"})
    print(json.dumps(cases, indent=2, sort_keys=True))
    return 0 if all(case["status"] == "PASS" for case in cases) else 1


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if command == "smoke":
        return smoke()
    if command == "reverse-test":
        return reverse_test()
    print("usage: python -m reporting_pipeline.cli [smoke|reverse-test]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
