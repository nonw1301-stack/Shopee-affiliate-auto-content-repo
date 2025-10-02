"""Simple ETL to aggregate publish and upload metrics into a CSV for ML training.

Reads JSON files under OUTPUT_DIR/publish_metrics and upload_metrics_*.json and
produces a single CSV with fields: upload_id, video_id, status, parts_uploaded, part, attempts, avg_duration, timestamp
"""
import os
import json
import csv
from pathlib import Path


def aggregate(output_dir: str, out_csv: str = None):
    out_csv = out_csv or os.path.join(output_dir, "metrics_aggregated.csv")
    pm_dir = Path(output_dir) / "publish_metrics"
    rows = []
    if not pm_dir.exists():
        print("No publish_metrics found at", pm_dir)
        return out_csv

    # collect commit envelopes and upload metrics
    commit_files = list(pm_dir.glob("commit_*.json"))
    summary_files = list(pm_dir.glob("summary_*.json"))
    upload_metrics_files = list(pm_dir.glob("upload_metrics_*.json"))

    # map upload_id -> commit envelope
    commits = {}
    for cf in commit_files:
        try:
            j = json.loads(cf.read_text(encoding="utf-8"))
            commits[j.get("upload_id")] = j
        except Exception:
            continue

    summaries = {}
    for sf in summary_files:
        try:
            j = json.loads(sf.read_text(encoding="utf-8"))
            summaries[j.get("upload_id")] = j
        except Exception:
            continue

    uploads = {}
    for uf in upload_metrics_files:
        try:
            j = json.loads(uf.read_text(encoding="utf-8"))
            # filename upload_metrics_{upload_id}.json
            uid = uf.stem.split("upload_metrics_")[-1]
            uploads[uid] = j
        except Exception:
            continue

    # build rows per upload part
    for uid, parts in uploads.items():
        commit = commits.get(uid, {})
        summary = summaries.get(uid, {})
        video_id = commit.get("video_id") if isinstance(commit, dict) else None
        status = commit.get("status") if isinstance(commit, dict) else None
        for part, attempts in parts.items():
            durations = [a.get("duration", 0) for a in attempts]
            avg_duration = sum(durations) / len(durations) if durations else None
            rows.append({
                "upload_id": uid,
                "video_id": video_id,
                "status": status,
                "parts_uploaded": summary.get("parts_uploaded"),
                "part": part,
                "attempts": len(attempts),
                "avg_duration": avg_duration,
                "timestamp": summary.get("timestamp") or commit.get("timestamp"),
            })

    # write CSV
    keys = ["upload_id", "video_id", "status", "parts_uploaded", "part", "attempts", "avg_duration", "timestamp"]
    with open(out_csv, "w", encoding="utf-8", newline="") as cf:
        w = csv.DictWriter(cf, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print("Wrote aggregated metrics to", out_csv)
    return out_csv


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", default=os.getenv("OUTPUT_DIR", "./output"))
    p.add_argument("--out-csv", default=None)
    args = p.parse_args()
    aggregate(args.output_dir, args.out_csv)
