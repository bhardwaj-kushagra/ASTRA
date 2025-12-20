"""Phase 4: Compare heuristic vs zero-shot on manual adversarial samples.

Runs the Detection service in two modes (simple and zero-shot) and prints a
compact comparison table.

Usage:
  python tools/scripts/evaluate_adversarial_detectors.py --base-url http://127.0.0.1:8002

Notes:
- This script assumes the Detection service is already running.
- For fully-offline zero-shot runs, start Detection with ZERO_SHOT_MODEL_PATH set
  to astra-models/facebook-bart-large-mnli.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests


def set_detector(*, base_url: str, name: str, timeout: int) -> None:
    resp = requests.post(f"{base_url}/detector/{name}", timeout=timeout)
    resp.raise_for_status()


def detect(*, base_url: str, text: str, timeout: int) -> Dict[str, Any]:
    resp = requests.post(f"{base_url}/detect", json={"text": text}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def load_samples(samples_dir: Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for path in sorted(samples_dir.glob("*.txt")):
        items.append({"name": path.name, "path": str(path), "text": path.read_text(encoding="utf-8")})
    return items


def _fmt_cell(s: str, width: int) -> str:
    s = s.replace("\n", " ").strip()
    if len(s) <= width:
        return s.ljust(width)
    return (s[: max(0, width - 1)] + "…")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8002")
    parser.add_argument(
        "--samples-dir",
        default=str(Path(__file__).resolve().parents[2] / "data" / "samples" / "adversarial"),
    )
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parents[2] / "logs" / "adversarial_eval.json"),
    )
    args = parser.parse_args()

    samples_dir = Path(args.samples_dir)
    samples = load_samples(samples_dir)
    if not samples:
        raise SystemExit(f"No .txt samples found in: {samples_dir}")

    results: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url,
        "samples_dir": str(samples_dir),
        "samples": [],
    }

    # Run simple detector
    set_detector(base_url=args.base_url, name="simple", timeout=args.timeout)
    simple_by_name: Dict[str, Dict[str, Any]] = {}
    for s in samples:
        out = detect(base_url=args.base_url, text=s["text"], timeout=args.timeout)
        simple_by_name[s["name"]] = out

    # Run zero-shot detector
    set_detector(base_url=args.base_url, name="zero-shot", timeout=args.timeout)
    zero_by_name: Dict[str, Dict[str, Any]] = {}
    for s in samples:
        out = detect(base_url=args.base_url, text=s["text"], timeout=max(args.timeout, 120))
        zero_by_name[s["name"]] = out

    # Print comparison
    name_w = 34
    label_w = 14
    conf_w = 6

    header = (
        _fmt_cell("sample", name_w)
        + "  "
        + _fmt_cell("simple", label_w)
        + "  "
        + _fmt_cell("conf", conf_w)
        + "  "
        + _fmt_cell("zero-shot", label_w)
        + "  "
        + _fmt_cell("conf", conf_w)
    )
    print(header)
    print("-" * len(header))

    for s in samples:
        n = s["name"]
        a = simple_by_name.get(n, {})
        b = zero_by_name.get(n, {})

        a_label = str(a.get("label", ""))
        b_label = str(b.get("label", ""))
        a_conf = a.get("confidence")
        b_conf = b.get("confidence")

        line = (
            _fmt_cell(n, name_w)
            + "  "
            + _fmt_cell(a_label, label_w)
            + "  "
            + _fmt_cell(f"{a_conf:.3f}" if isinstance(a_conf, (int, float)) else "", conf_w)
            + "  "
            + _fmt_cell(b_label, label_w)
            + "  "
            + _fmt_cell(f"{b_conf:.3f}" if isinstance(b_conf, (int, float)) else "", conf_w)
        )
        print(line)

        results["samples"].append(
            {
                "name": n,
                "simple": a,
                "zero_shot": b,
            }
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("")
    print(f"Wrote report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
