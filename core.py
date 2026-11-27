from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image

SUPPORTED_CHART_TYPES = {"bar", "horizontal_bar", "line", "lollipop"}


def load_tasks(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        tasks = json.load(f)
    if not isinstance(tasks, list):
        raise ValueError("Task dataset must be a JSON list.")
    return tasks


def resolve_image_path(task: dict[str, Any], dataset_path: str | Path) -> Path:
    """Resolve image paths relative to the directory containing the dataset."""
    raw = Path(str(task.get("image", "")))
    if raw.is_absolute():
        return raw
    return Path(dataset_path).resolve().parent / raw


def expected_answer(task: dict[str, Any], question: dict[str, Any]) -> Any:
    data = task.get("data")
    categories = task.get("categories")
    if not isinstance(data, dict) or not data:
        raise ValueError("Missing or empty task data.")
    if not isinstance(categories, list) or not categories:
        raise ValueError("Missing task categories.")
    if set(categories) != set(data.keys()):
        raise ValueError("Categories and data keys do not match.")

    qtype = question.get("question_type")
    params = question.get("parameters") or {}
    values = list(data.values())
    ordered = sorted(data, key=data.get, reverse=True)

    if qtype == "highest_category":
        return ordered[0]
    if qtype == "second_highest":
        if len(ordered) < 2:
            raise ValueError("At least two categories are required.")
        return ordered[1]
    if qtype == "value_lookup":
        return data[params["category"]]
    if qtype == "absolute_difference":
        return abs(data[params["category_a"]] - data[params["category_b"]])
    if qtype == "count_above_threshold":
        threshold = params["threshold"]
        return sum(value > threshold for value in values)
    if qtype == "total_value":
        return sum(values)
    if qtype == "largest_step_change":
        ordered_values = [data[category] for category in categories]
        changes = [
            abs(ordered_values[i + 1] - ordered_values[i])
            for i in range(len(ordered_values) - 1)
        ]
        if not changes:
            raise ValueError("At least two sequential values are required.")
        max_change = max(changes)
        if changes.count(max_change) > 1:
            raise ValueError("Largest step change is tied and ambiguous.")
        i = changes.index(max_change)
        return f"{categories[i]} to {categories[i + 1]}"

    raise ValueError(f"Unsupported question type: {qtype!r}")


def validate_task(
    task: dict[str, Any],
    dataset_path: str | Path,
    check_image: bool = True,
) -> list[str]:
    errors: list[str] = []
    task_id = task.get("task_id")

    if not task_id:
        errors.append("Missing task_id")
    if task.get("chart_type") not in SUPPORTED_CHART_TYPES:
        errors.append("Unsupported or missing chart_type")

    data = task.get("data")
    categories = task.get("categories")
    questions = task.get("questions")

    if not isinstance(data, dict) or not data:
        errors.append("Missing or empty data")
        data = {}
    if not isinstance(categories, list) or not categories:
        errors.append("Missing or empty categories")
        categories = []
    if isinstance(data, dict) and isinstance(categories, list):
        if set(categories) != set(data.keys()):
            errors.append("Categories and data keys do not match")
        if len(set(data.values())) != len(data):
            errors.append("Tied values create ranking ambiguity")

    if not isinstance(questions, list) or not questions:
        errors.append("Missing or empty questions")
        questions = []
    elif len(questions) != 6:
        errors.append(f"Expected 6 questions; found {len(questions)}")

    question_ids = [q.get("question_id") for q in questions if isinstance(q, dict)]
    if len(question_ids) != len(set(question_ids)):
        errors.append("Duplicate question IDs")

    for q in questions:
        if not isinstance(q, dict):
            errors.append("Question entry is not an object")
            continue
        try:
            expected = expected_answer(task, q)
            if q.get("answer") != expected:
                errors.append(
                    f"Incorrect reference answer for {q.get('question_type', 'unknown')}"
                )
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            errors.append(
                f"Invalid {q.get('question_type', 'unknown')} question: {exc}"
            )

    if check_image:
        image_path = resolve_image_path(task, dataset_path)
        if not image_path.is_file():
            errors.append(f"Missing image file: {image_path}")
        else:
            try:
                with Image.open(image_path) as image:
                    image.verify()
                with Image.open(image_path) as image:
                    if image.width < 200 or image.height < 150:
                        errors.append("Image dimensions are unexpectedly small")
            except Exception as exc:
                errors.append(f"Invalid image file: {exc}")

    return errors


def validate_dataset(
    tasks: list[dict[str, Any]],
    dataset_path: str | Path,
    check_images: bool = True,
) -> list[dict[str, Any]]:
    ids = [task.get("task_id") for task in tasks]
    seen = set()
    duplicates = set()
    for task_id in ids:
        if task_id in seen:
            duplicates.add(task_id)
        seen.add(task_id)

    results = []
    for task in tasks:
        errors = validate_task(task, dataset_path, check_image=check_images)
        if task.get("task_id") in duplicates:
            errors.append("Duplicate task ID")
        results.append({
            "task_id": task.get("task_id"),
            "status": "PASS" if not errors else "FAIL",
            "errors": errors,
        })
    return results
