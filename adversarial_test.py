#!/usr/bin/env python3
"""Run controlled fault-injection checks against the V2 validator."""

import argparse
import copy
import json
from pathlib import Path

from zeroshortcut.core import load_tasks, validate_dataset, validate_task


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="data/visual_tasks_v2.json")
    parser.add_argument("--report", default="reports/adversarial_validation_v2.json")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    tasks = load_tasks(dataset_path)
    if not tasks:
        raise SystemExit("Dataset is empty")

    # 1. Incorrect reference answer
    wrong = copy.deepcopy(tasks[0])
    wrong["questions"][0]["answer"] = "INTENTIONALLY_WRONG"
    wrong_detected = any("Incorrect reference answer" in e for e in validate_task(wrong, dataset_path, check_image=False))

    # 2. Missing image file
    missing = copy.deepcopy(tasks[0])
    missing["image"] = "images_v2/__intentionally_missing__.png"
    missing_errors = validate_task(missing, dataset_path, check_image=True)
    missing_detected = any("Missing image file" in e for e in missing_errors)

    # 3. Duplicate task ID in a dataset
    duplicate = copy.deepcopy(tasks[0])
    duplicate_results = validate_dataset([tasks[0], duplicate], dataset_path, check_images=False)
    duplicate_detected = any("Duplicate task ID" in e for r in duplicate_results for e in r["errors"])

    # 4. Tied values should be rejected as ambiguous
    tied = copy.deepcopy(tasks[0])
    categories = tied["categories"]
    tied["data"][categories[1]] = tied["data"][categories[0]]
    tie_errors = validate_task(tied, dataset_path, check_image=False)
    tie_detected = any("Tied values create ranking ambiguity" in e for e in tie_errors)

    checks = {
        "incorrect_answer_detection": wrong_detected,
        "missing_image_detection": missing_detected,
        "duplicate_id_detection": duplicate_detected,
        "ambiguous_tie_detection": tie_detected,
    }
    passed = sum(checks.values())
    report = {
        "module": "Adversarial Validation",
        "dataset": str(dataset_path),
        "base_tasks": len(tasks),
        "adversarial_tests": checks,
        "adversarial_tests_passed": passed,
        "adversarial_tests_total": len(checks),
        "all_adversarial_tests_passed": passed == len(checks),
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("ZEROSHORTCUT - ADVERSARIAL VALIDATION")
    for name, detected in checks.items():
        print(name, ":", "DETECTED" if detected else "MISSED")
    print("Passed:", passed, "/", len(checks))
    print("Report:", report_path)
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
