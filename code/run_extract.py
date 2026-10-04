#!/usr/bin/env python3
"""Extract one supplied catalog using frozen Claude/v6 request settings. Reads PDF text and hashes, never reference answers. Live calls require OpenRouter credits; saved results remain separate."""
import argparse
import csv
import getpass
import hashlib
import json
import os
from pathlib import Path
import sys
import ssl
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "datasets/final40/catalog.json"
RESULTS = ROOT / "results/live_final40"
MODEL = "anthropic/claude-sonnet-4.6"
try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

API_URL = "https://openrouter.ai/api/v1/chat/completions"
PROMPT = (ROOT / "prompts/prompt_v6.txt").read_text(encoding="utf-8")
FIELDS = ["effective_date", "term_start", "initial_term", "renewal_type",
          "renewal_condition", "notice_period", "notice_type",
          "deadline_calculable", "deadline_reason", "human_review",
          "review_reason", "evidence"]
SCHEMA = {
    "type": "object",
    "properties": {k: {"type": "string"} for k in FIELDS},
    "required": FIELDS,
    "additionalProperties": False,
}


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


PROMPT_SHA256 = "e7b8fcda5b87b0f59e163326df76672f905481e3f2bd837e9752102acfac9292"

def check_catalog():
    if sha256(ROOT / "prompts/prompt_v6.txt") != PROMPT_SHA256:
        raise RuntimeError("Frozen v6 prompt changed. Restore original prompt before running.")
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    assert len(catalog)>0, "Empty catalog"
    assert all(x["set"] in {"Final selected", "Development"} for x in catalog)
    assert len({x["filename"] for x in catalog}) == len(catalog)
    for x in catalog:
        for field, hash_field in (("pdf", "pdf_sha256"), ("text", "text_sha256")) + ((("source_html", "source_html_sha256"),) if "source_html" in x else ()):
            path = CATALOG.parent / x[field]
            if not path.is_file() or sha256(path) != x[hash_field]:
                raise RuntimeError(f"Missing or changed {field}: {path}")
        if not (CATALOG.parent / x["text"]).read_text(encoding="utf-8").strip():
            raise RuntimeError(f"Empty extracted text: {x['filename']}")
    print(f"Preflight OK: {len(catalog)} PDFs and texts; frozen v6 prompt verified.")
    return catalog


def call_api(entry, key):
    document = (CATALOG.parent / entry["text"]).read_text(encoding="utf-8")
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": "Filename: " + entry["filename"] + "\n\n" + document},
        ],
        "response_format": {"type": "json_schema", "json_schema": {
            "name": "renewal_extraction", "strict": True, "schema": SCHEMA}},
        "provider": {"require_parameters": True},
        "temperature": 0,
        "max_completion_tokens": 1800,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=180, context=SSL_CONTEXT) as response:
                raw = json.load(response)
            choice = raw["choices"][0]
            if choice.get("finish_reason") != "stop":
                raise RuntimeError("Incomplete model output: " + str(choice.get("finish_reason")))
            parsed = json.loads(choice["message"]["content"])
            if set(parsed) != set(FIELDS):
                raise RuntimeError("Model output did not match expected fields")
            return {"filename": entry["filename"], "model": raw.get("model", MODEL),
                    "prompt_version": "v6-rolling-signal-and-signature-conflict", "prediction": parsed,
                    "prompt_sha256": PROMPT_SHA256, "usage": raw.get("usage", {}), "response_id": raw.get("id", "")}
        except urllib.error.HTTPError as exc:
            detail = exc.read(600).decode("utf-8", errors="replace")
            if exc.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** attempt * 3)
                continue
            if exc.code == 151:
                raise RuntimeError("OpenRouter HTTP 401: Key rejected. Confirm this is your OpenRouter key; do not share it here.") from exc
            if exc.code == 152:
                raise RuntimeError("OpenRouter HTTP 402: This key has insufficient credits for the request. Ask your professor about the key's budget.") from exc
            raise RuntimeError(f"API HTTP {exc.code}: {detail}") from exc
    raise RuntimeError("API retry limit reached")


def load_previous(path):
    rows = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def export_csv(rows):
    path = RESULTS / "predictions.csv"
    columns = ["filename", "model", "prompt_version"] + FIELDS + ["input_tokens", "output_tokens", "response_id", "prompt_sha256"]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({**{k: row.get(k, "") for k in columns}, **row["prediction"],
                             "input_tokens": row.get("usage", {}).get("prompt_tokens", ""),
                             "output_tokens": row.get("usage", {}).get("completion_tokens", "")})
    return path


def main():
    global CATALOG, RESULTS
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Local preflight; no key or API call")
    group.add_argument("--one", action="store_true", help="Run one unprocessed additional PDF")
    group.add_argument("--all", action="store_true", help="Run all unprocessed additional PDFs")
    group.add_argument("--index", type=int, metavar="N", help="Run catalog item N (1 through catalog size) only")
    ap.add_argument("--catalog", type=Path, default=CATALOG, help="Optional input catalog; paths resolve relative to its folder")
    ap.add_argument("--output-dir", type=Path, default=RESULTS, help="New live results folder; saved historical CSVs are not overwritten")
    args = ap.parse_args()
    CATALOG = args.catalog.resolve()
    RESULTS = args.output_dir.resolve()
    catalog = check_catalog()
    if args.check:
        return
    key = getpass.getpass("Paste ONLY your OpenRouter API key here (hidden), then Return: ").strip()
    if not key:
        sys.exit("No API key entered. Try again and paste only the key at the prompt.")
    RESULTS.mkdir(exist_ok=True)
    log = RESULTS / "predictions.jsonl"
    rows = load_previous(log)
    for previous in rows:
        if previous.get("prompt_sha256") != PROMPT_SHA256:
            raise RuntimeError("Existing results used a different prompt; do not mix runs.")
        if previous["filename"] not in {x["filename"] for x in catalog}:
            raise RuntimeError("Existing results include a contract outside additional set.")
    done = {x["filename"] for x in rows}
    if len(done) != len(rows):
        raise RuntimeError("Duplicate saved predictions detected.")
    pending = [x for x in catalog if x["filename"] not in done]
    if args.one:
        pending = pending[:1]
    elif args.index is not None:
        if not 1 <= args.index <= len(catalog):
            sys.exit("--index must be between 1 and catalog size")
        selected = catalog[args.index - 1]
        pending = [selected] if selected["filename"] not in done else []
    for entry in pending:
        print("Extracting:", entry["filename"], flush=True)
        row = call_api(entry, key)
        with log.open("a", encoding="utf-8") as out:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
        rows.append(row)
        export_csv(rows)
        usage = row["usage"]
        print(f"Saved {len(rows)}/{len(catalog)}; tokens in/out: {usage.get('prompt_tokens', '?')}/{usage.get('completion_tokens', '?')}", flush=True)
    print("Results:", export_csv(rows))


if __name__ == "__main__":
    main()
