#!/usr/bin/env python3
"""Validate task reference answers, dataset structure, and image files."""

import argparse
import json
from pathlib import Path

from zeroshortcut.core import load_tasks, validate_dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="data/visual_tasks_v2.json")
    parser.add_argument("--report", default="reports/validation_report_v2.json")
    parser.add_argument("--skip-images", action="store_true", help="Skip image file checks")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    tasks = load_tasks(dataset_path)
    results = validate_dataset(tasks, dataset_path, check_images=not args.skip_images)
    passed = sum(r["status"] == "PASS" for r in results)
    failed = len(results) - passed

    report = {
        "dataset": str(dataset_path),
        "total_tasks": len(tasks),
        "passed": passed,
        "failed": failed,
        "results": results,
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("ZEROSHORTCUT - REFERENCE VALIDATION")
    print("Total tasks:", len(tasks))
    print("Passed:", passed)
    print("Failed:", failed)
    print("Report:", report_path)
    if failed:
        for result in results:
            if result["errors"]:
                print(result["task_id"], "->", "; ".join(result["errors"]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
