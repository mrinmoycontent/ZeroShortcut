#!/usr/bin/env python3
"""Generate a reproducible V2 synthetic visual-task dataset."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CHART_TYPES = ["bar", "horizontal_bar", "line", "lollipop"]
REGIONS = ["North", "South", "East", "West", "Central", "Coastal", "Metro"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
METRICS = ["Sales (₹ lakh)", "Orders", "Service tickets", "Units sold"]


def sample_values(rng: random.Random, number: int, chart_type: str) -> list[int]:
    """Sample distinct values; line charts must have one unique largest step.

    This avoids generating an ambiguous largest_step_change reference answer.
    """
    while True:
        values = rng.sample(range(120, 981), number)
        if chart_type != "line":
            return values
        changes = [abs(values[i + 1] - values[i]) for i in range(len(values) - 1)]
        if changes and changes.count(max(changes)) == 1:
            return values


def create_questions(categories, values, task_id, chart_type, rng):
    data = dict(zip(categories, values))
    ordered = sorted(data, key=data.get, reverse=True)
    questions = [
        {"question_id": f"{task_id}_Q1", "question_type": "highest_category",
         "question": "Which category has the highest value?", "answer": ordered[0]},
        {"question_id": f"{task_id}_Q2", "question_type": "second_highest",
         "question": "Which category ranks second highest?", "answer": ordered[1]},
    ]

    target = rng.choice(categories)
    questions.append({
        "question_id": f"{task_id}_Q3", "question_type": "value_lookup",
        "question": f"What is the value for {target}?", "answer": data[target],
        "parameters": {"category": target},
    })

    pair = rng.sample(categories, 2)
    questions.append({
        "question_id": f"{task_id}_Q4", "question_type": "absolute_difference",
        "question": f"What is the absolute difference between {pair[0]} and {pair[1]}?",
        "answer": abs(data[pair[0]] - data[pair[1]]),
        "parameters": {"category_a": pair[0], "category_b": pair[1]},
    })

    threshold = int(statistics.median(values))
    questions.append({
        "question_id": f"{task_id}_Q5", "question_type": "count_above_threshold",
        "question": f"How many categories have a value greater than {threshold}?",
        "answer": sum(value > threshold for value in values),
        "parameters": {"threshold": threshold},
    })

    if chart_type == "line":
        changes = [abs(values[i + 1] - values[i]) for i in range(len(values) - 1)]
        index = changes.index(max(changes))
        answer = f"{categories[index]} to {categories[index + 1]}"
        questions.append({
            "question_id": f"{task_id}_Q6", "question_type": "largest_step_change",
            "question": "Between which consecutive periods does the largest absolute change occur?",
            "answer": answer,
        })
    else:
        questions.append({
            "question_id": f"{task_id}_Q6", "question_type": "total_value",
            "question": "What is the total value across all categories?",
            "answer": sum(values),
        })
    return questions


def draw_chart(task_id, chart_type, categories, values, metric, image_path):
    fig, ax = plt.subplots(figsize=(9, 5))
    if chart_type == "bar":
        bars = ax.bar(categories, values)
        ax.bar_label(bars, padding=3)
    elif chart_type == "horizontal_bar":
        bars = ax.barh(categories, values)
        ax.bar_label(bars, padding=3)
        ax.set_xlim(0, max(values) * 1.25)
    elif chart_type == "line":
        ax.plot(categories, values, marker="o", linewidth=2)
        for category, value in zip(categories, values):
            ax.annotate(str(value), (category, value), xytext=(0, 7), textcoords="offset points", ha="center")
    elif chart_type == "lollipop":
        positions = list(range(len(categories)))
        ax.vlines(positions, 0, values)
        ax.scatter(positions, values, s=65)
        ax.set_xticks(positions)
        ax.set_xticklabels(categories)
        for x, value in zip(positions, values):
            ax.annotate(str(value), (x, value), xytext=(0, 7), textcoords="offset points", ha="center")
    ax.set_title(f"{metric} Comparison - {task_id}")
    ax.set_ylabel(metric)
    ax.set_xlabel("Month" if chart_type == "line" else "Category")
    if chart_type != "horizontal_bar":
        ax.set_ylim(0, max(values) * 1.25)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(image_path, dpi=160)
    plt.close(fig)


def generate_dataset(output_dir: Path, count: int = 24, seed: int = 20261123):
    rng = random.Random(seed)
    image_dir = output_dir / "images_v2"
    image_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks = []

    for i in range(count):
        task_id = f"ZS2_{i + 1:03d}"
        chart_type = CHART_TYPES[i % len(CHART_TYPES)]
        if chart_type == "line":
            start = rng.randint(0, 3)
            number = rng.choice([6, 7, 8])
            categories = MONTHS[start:start + number]
        else:
            number = rng.choice([5, 6, 7])
            categories = rng.sample(REGIONS, number)
        values = sample_values(rng, len(categories), chart_type)
        metric = rng.choice(METRICS)
        image_name = f"{task_id}.png"
        draw_chart(task_id, chart_type, categories, values, metric, image_dir / image_name)
        tasks.append({
            "task_id": task_id,
            "generation_version": "2.0",
            "chart_type": chart_type,
            "metric": metric,
            "image": f"images_v2/{image_name}",
            "categories": categories,
            "data": dict(zip(categories, values)),
            "questions": create_questions(categories, values, task_id, chart_type, rng),
        })

    dataset_path = output_dir / "visual_tasks_v2.json"
    dataset_path.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Generated tasks: {len(tasks)}")
    print(f"Generated questions: {sum(len(t['questions']) for t in tasks)}")
    print(f"Chart distribution: {dict(Counter(t['chart_type'] for t in tasks))}")
    print(f"Dataset: {dataset_path}")
    print(f"Images: {image_dir}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="data", help="Output data directory (default: data)")
    parser.add_argument("--count", type=int, default=24, help="Number of tasks to generate")
    parser.add_argument("--seed", type=int, default=20261123, help="Random seed")
    args = parser.parse_args()
    if args.count < 4:
        parser.error("--count must be at least 4 to cover all four chart families")
    generate_dataset(Path(args.output_dir), args.count, args.seed)


if __name__ == "__main__":
    main()
