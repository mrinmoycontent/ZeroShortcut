#!/usr/bin/env python3
"""Evaluate the packaged visual tasks with OpenRouter (resumable per task).

Set OPENROUTER_API_KEY in the environment. This script never stores the API key.
The default model matches the completed benchmark included with this repository.
"""
from __future__ import annotations
import argparse, base64, json, os, re, time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
import requests
from zeroshortcut.core import load_tasks

MODEL_DEFAULT = "nvidia/nemotron-3.5-super-vl:free"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

MONTH_ALIASES = {"jan":"january","feb":"february","mar":"march","apr":"april","may":"may","jun":"june","jul":"july","aug":"august","sep":"september","oct":"october","nov":"november","dec":"december"}

def normalize_text(value: object) -> str:
    text = str(value).strip().casefold()
    text = re.sub(r"\s*(?:→|–|—|-)\s*", " to ", text)
    for short, full in MONTH_ALIASES.items():
        text = re.sub(rf"\b{short}\b", full, text)
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    return " ".join(text.split())

def compare(expected: object, predicted: object) -> bool:
    if predicted is None:
        return False
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        try:
            expected_num = Decimal(str(expected))
            matches = re.findall(r"-?\d[\d,]*(?:\.\d+)?", str(predicted))
            return bool(matches) and Decimal(matches[0].replace(",", "")) == expected_num
        except (InvalidOperation, ValueError):
            return False
    return normalize_text(expected) == normalize_text(predicted)

def parse_response(content: str) -> dict:
    clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.I)
    start, end = clean.find("{"), clean.rfind("}")
    if start < 0 or end < start:
        raise ValueError("Model response did not contain a JSON object")
    parsed = json.loads(clean[start:end+1])
    if not isinstance(parsed.get("answers"), list):
        raise ValueError("Model JSON must contain an answers array")
    return parsed

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="data/visual_tasks_v2.json")
    parser.add_argument("--output-dir", default="evaluations/nemotron")
    parser.add_argument("--model", default=MODEL_DEFAULT)
    parser.add_argument("--task-id", help="Evaluate only this task ID")
    parser.add_argument("--resume", action="store_true", help="Skip tasks with six saved scored answers")
    parser.add_argument("--delay", type=float, default=3.5, help="Seconds between requests")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("Set OPENROUTER_API_KEY in the environment; do not hard-code it.")

    dataset_path = Path(args.dataset)
    tasks = load_tasks(dataset_path)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    selected = [t for t in tasks if not args.task_id or t["task_id"] == args.task_id]
    if args.task_id and not selected:
        raise SystemExit(f"Unknown task ID: {args.task_id}")

    session = requests.Session()
    for index, task in enumerate(selected, 1):
        task_id = task["task_id"]
        raw_path = out / f"{task_id}.json"
        score_path = out / f"{task_id}_scored.json"
        if args.resume and score_path.exists():
            try:
                prior = json.loads(score_path.read_text(encoding="utf-8"))
                ids = {r.get("question_id") for r in prior.get("results", [])}
                expected_ids = {q["question_id"] for q in task["questions"]}
                if ids == expected_ids and len(prior.get("results", [])) == len(expected_ids):
                    print(f"[{index}/{len(selected)}] {task_id}: skipped (complete)")
                    continue
            except Exception:
                pass

        image_path = Path(args.dataset).resolve().parent / task["image"]
        if not image_path.is_file():
            raise FileNotFoundError(image_path)
        image_b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
        question_payload = [{"question_id": q["question_id"], "question": q["question"]} for q in task["questions"]]
        prompt = (
            "You are participating in a visual chart understanding benchmark. "
            "Study the attached chart and answer using only information visible in it. "
            "Do not use external knowledge or invent values. Use exact category labels. "
            "Return valid JSON only in this format: "
            '{"answers":[{"question_id":"...","answer":"..."}]}\nQuestions:\n'
            + json.dumps(question_payload, ensure_ascii=False)
        )
        payload = {
            "model": args.model,
            "messages": [{"role":"user","content":[
                {"type":"text","text":prompt},
                {"type":"image_url","image_url":{"url":"data:image/png;base64," + image_b64}}
            ]}],
            "max_tokens": 2048,
            "temperature": 0,
            "reasoning_effort": "none",
            "provider": {"options":{"chat_template_kwargs":{"enable_thinking":False}}}
        }
        print(f"[{index}/{len(selected)}] Evaluating {task_id}...", flush=True)
        response = session.post(ENDPOINT, headers={"Authorization":"Bearer " + api_key,"Content-Type":"application/json"}, json=payload, timeout=(15,args.timeout))
        print("HTTP:", response.status_code)
        response.raise_for_status()
        raw = response.json()
        raw_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        choice = raw["choices"][0]
        content = choice["message"].get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(f"Empty model response for {task_id}; raw response saved to {raw_path}")
        parsed = parse_response(content)
        predicted = {a.get("question_id"): a.get("answer") for a in parsed["answers"]}
        expected_ids = {q["question_id"] for q in task["questions"]}
        if set(predicted) != expected_ids:
            raise RuntimeError(f"Question IDs mismatch for {task_id}; raw response preserved")
        results = []
        for q in task["questions"]:
            answer = predicted[q["question_id"]]
            results.append({"question_id":q["question_id"],"question_type":q["question_type"],"question":q["question"],"reference_answer":q["answer"],"model_answer":answer,"correct":compare(q["answer"],answer)})
        correct = sum(r["correct"] for r in results)
        scored = {"task_id":task_id,"chart_type":task["chart_type"],"model":raw.get("model",args.model),"evaluation_status":"completed","timestamp":datetime.now(timezone.utc).isoformat(),"correct_answers":correct,"incorrect_answers":len(results)-correct,"total_questions":len(results),"accuracy_percent":round(correct/len(results)*100,2),"results":results,"finish_reason":choice.get("finish_reason"),"usage":raw.get("usage")}
        score_path.write_text(json.dumps(scored, indent=2), encoding="utf-8")
        print(f"{task_id}: {correct}/{len(results)} ({scored['accuracy_percent']}%)")
        if index < len(selected):
            time.sleep(max(0, args.delay))

if __name__ == "__main__":
    main()
