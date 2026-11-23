import copy
from pathlib import Path

from zeroshortcut.core import load_tasks, validate_dataset, validate_task

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "visual_tasks_v2.json"


def test_packaged_dataset_exists_and_loads():
    tasks = load_tasks(DATASET)
    assert len(tasks) == 24


def test_all_packaged_tasks_pass_reference_and_image_validation():
    tasks = load_tasks(DATASET)
    results = validate_dataset(tasks, DATASET, check_images=True)
    assert len(results) == 24
    assert all(result["status"] == "PASS" for result in results)


def test_wrong_reference_answer_is_detected():
    task = copy.deepcopy(load_tasks(DATASET)[0])
    task["questions"][0]["answer"] = "WRONG"
    errors = validate_task(task, DATASET, check_image=False)
    assert any("Incorrect reference answer" in error for error in errors)


def test_tied_values_are_detected():
    task = copy.deepcopy(load_tasks(DATASET)[0])
    categories = task["categories"]
    task["data"][categories[1]] = task["data"][categories[0]]
    errors = validate_task(task, DATASET, check_image=False)
    assert any("Tied values create ranking ambiguity" in error for error in errors)


def test_missing_image_is_detected():
    task = copy.deepcopy(load_tasks(DATASET)[0])
    task["image"] = "images_v2/__missing_test_file__.png"
    errors = validate_task(task, DATASET, check_image=True)
    assert any("Missing image file" in error for error in errors)


def test_duplicate_task_ids_are_detected():
    tasks = load_tasks(DATASET)
    results = validate_dataset([tasks[0], copy.deepcopy(tasks[0])], DATASET, check_images=False)
    assert any(
        "Duplicate task ID" in error
        for result in results
        for error in result["errors"]
    )


def test_line_generator_has_unique_largest_step_across_seeds():
    import random
    from generate import sample_values

    for seed in range(100):
        values = sample_values(random.Random(seed), 8, "line")
        changes = [abs(values[i + 1] - values[i]) for i in range(len(values) - 1)]
        assert changes.count(max(changes)) == 1


def test_non_line_generator_returns_distinct_values():
    import random
    from generate import sample_values

    values = sample_values(random.Random(7), 7, "bar")
    assert len(values) == 7
    assert len(set(values)) == 7
