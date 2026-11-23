#!/usr/bin/env python3
"""Create a consolidated offline evidence report from task data and test reports."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from zeroshortcut.core import load_tasks, resolve_image_path, validate_dataset


def read_json(path):
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="data/visual_tasks_v2.json")
    parser.add_argument("--report-dir", default="reports")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    tasks = load_tasks(dataset_path)
    validations = validate_dataset(tasks, dataset_path, check_images=True)
    adversarial_path = report_dir / "adversarial_validation_v2.json"
    adversarial = read_json(adversarial_path) if adversarial_path.exists() else None

    chart_distribution = Counter(task.get("chart_type", "unknown") for task in tasks)
    question_distribution = Counter(
        question.get("question_type", "unknown")
        for task in tasks for question in task.get("questions", [])
    )
    signatures = {tuple(sorted(task.get("data", {}).items())) for task in tasks}
    valid_images = sum(resolve_image_path(task, dataset_path).is_file() for task in tasks)
    total_questions = sum(len(task.get("questions", [])) for task in tasks)
    passed = sum(result["status"] == "PASS" for result in validations)
    failed = len(validations) - passed

    summary = {
        "project": "ZeroShortcut",
        "report_version": "2.1",
        "dataset_version": "V2",
        "total_tasks": len(tasks),
        "total_questions": total_questions,
        "valid_images": valid_images,
        "unique_datasets": len(signatures),
        "chart_distribution": dict(chart_distribution),
        "question_distribution": dict(question_distribution),
        "reference_validation": {"passed": passed, "failed": failed},
        "adversarial_validation": adversarial,
        "ai_model_evaluation": {
            "status": "Not completed",
            "model_accuracy": None,
            "reason": "No external model benchmark report was found at report-generation time.",
        },
    }
    model_report_path = report_dir / "nemotron_final_benchmark.json"
    if model_report_path.exists():
        model_report = read_json(model_report_path)
        overall = model_report.get("overall_results", {})
        summary["ai_model_evaluation"] = {
            "status": model_report.get("evaluation_status", "available"),
            "model": model_report.get("model"),
            "model_accuracy": overall.get("accuracy_percent"),
            "correct": overall.get("correct"),
            "incorrect": overall.get("incorrect"),
            "questions_evaluated": overall.get("total"),
            "source_report": str(model_report_path),
        }

    (report_dir / "benchmark_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    inventory = []
    for task, result in zip(tasks, validations):
        image_path = resolve_image_path(task, dataset_path)
        inventory.append({
            "task_id": task.get("task_id"),
            "version": "V2",
            "chart_type": task.get("chart_type"),
            "question_count": len(task.get("questions", [])),
            "image_status": "VALID" if image_path.is_file() else "MISSING",
            "validation_status": result["status"],
            "errors": "; ".join(result["errors"]),
        })
    with (report_dir / "task_inventory.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(inventory[0].keys()) if inventory else ["task_id"])
        writer.writeheader()
        writer.writerows(inventory)

    md = [
        "# ZeroShortcut – Consolidated Benchmark Report",
        "",
        "## Dataset summary",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Visual tasks | {len(tasks)} |",
        f"| Questions | {total_questions} |",
        f"| Valid image files | {valid_images} |",
        f"| Unique source datasets | {len(signatures)} |",
        f"| Reference validation passed | {passed} |",
        f"| Reference validation failed | {failed} |",
        "",
        "## Chart distribution",
        "",
        "| Chart type | Count |",
        "|---|---:|",
    ]
    md.extend(f"| {name} | {count} |" for name, count in chart_distribution.items())
    md += ["", "## Question distribution", "", "| Question type | Count |", "|---|---:|"]
    md.extend(f"| {name} | {count} |" for name, count in question_distribution.items())
    md += ["", "## Adversarial validation", ""]
    if adversarial:
        md.append(f"Passed: {adversarial.get('adversarial_tests_passed', 0)}/{adversarial.get('adversarial_tests_total', 0)}")
        md += ["", "| Test | Result |", "|---|---|"]
        md.extend(
            f"| {name} | {'DETECTED' if detected else 'MISSED'} |"
            for name, detected in adversarial.get("adversarial_tests", {}).items()
        )
    else:
        md.append("Adversarial test report not found. Run `python adversarial_test.py`.")
    md += [
        "",
        "## AI model evaluation",
        "",
        (
            f"Completed: {model_report.get('model')} achieved "
            f"{model_report.get('overall_results', {}).get('accuracy_percent')}% "
            f"({model_report.get('overall_results', {}).get('correct')}/"
            f"{model_report.get('overall_results', {}).get('total')} correct)."
            if model_report_path.exists() else
            "No external model benchmark report is available yet."
        ),
        "",
        "## Limitations",
        "",
        "- The current task family focuses on synthetic business-chart interpretation.",
        "- Reference answers are compared against the source data embedded in each task.",
        "- The adversarial suite covers four deliberately injected fault types.",
        "- Only one external model has been evaluated; a second-model comparison remains outstanding.",
        "- Results are specific to this synthetic chart dataset and do not establish broad visual reasoning performance.",
        "",
    ]
    (report_dir / "benchmark_report.md").write_text("\n".join(md), encoding="utf-8")

    print("ZEROSHORTCUT - CONSOLIDATED REPORT")
    print("Tasks:", len(tasks))
    print("Questions:", total_questions)
    print("Valid images:", valid_images)
    print("Reference validation:", passed, "/", len(tasks))
    print("Reports written to:", report_dir)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
