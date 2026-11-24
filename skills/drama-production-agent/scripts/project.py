"""Local project scaffold and evidence completeness check. No network or media calls."""
import argparse
import hashlib
import json
from pathlib import Path

STATES = {"planned", "submitting", "submitted", "submission_unknown", "retrieved",
          "accepted", "failed", "needs_review", "stale"}
CHECKS = {"image": {"technical", "visual"}, "audio": {"technical", "audio"},
          "video": {"technical", "visual", "audio"}}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect(root):
    data = json.loads((root / "project.json").read_text(encoding="utf-8"))
    errors, selected_issues = [], []
    if data.get("schema_version") != 1:
        errors.append("Unsupported schema_version")
    actions = data.get("actions", [])
    selected = data.get("deliverables", [])
    if not isinstance(actions, list) or not isinstance(selected, list):
        raise ValueError("actions and deliverables must be lists")
    records = {}
    issues = {}
    for item in actions:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            errors.append("Every action requires a nonempty string id")
            continue
        key = item["id"]
        if key in records:
            errors.append(f"Duplicate action id: {key}")
        records[key] = item
        issues[key] = []
    for key, item in records.items():
        bad = issues[key]
        if item.get("state") not in STATES:
            errors.append(f"{key}: invalid state")
        deps = item.get("depends_on", [])
        if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
            errors.append(f"{key}: depends_on must contain string IDs")
            continue
        for dep in deps:
            if dep not in records:
                errors.append(f"{key}: missing dependency {dep}")
        if item.get("state") != "accepted":
            bad.append(f"state={item.get('state')}; not accepted")
        if item.get("state") in {"submitting", "submission_unknown"}:
            bad.append("Reconcile provider outcome before any resubmission")
        if item.get("state") not in {"retrieved", "accepted"}:
            continue
        kind = item.get("kind")
        if kind not in CHECKS:
            bad.append("Unsupported media kind")
            continue
        relpath = item.get("path")
        if not isinstance(relpath, str) or not relpath:
            bad.append("Missing media path")
            continue
        path = (root / relpath).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            bad.append("Media file missing or outside project")
            continue
        digest = sha256(path)
        if digest != item.get("sha256"):
            bad.append("Media SHA-256 mismatch")
        qa = item.get("qa", [])
        if not isinstance(qa, list):
            bad.append("qa must be a list")
            continue
        for check in CHECKS[kind]:
            matches = [q for q in qa if isinstance(q, dict) and q.get("check") == check]
            if len(matches) != 1:
                bad.append(f"{check}: exactly one current review record required")
                continue
            review = matches[0]
            evidence = review.get("evidence")
            allowed = {"pass", "not_applicable"} if check == "audio" and kind == "video" else {"pass"}
            if review.get("result") not in allowed:
                bad.append(f"{check}: not passed")
            if not isinstance(evidence, str) or not evidence.strip():
                bad.append(f"{check}: missing observation evidence")
            if review.get("sha256") != digest:
                bad.append(f"{check}: review does not match actual media")

    visited, active, closure = set(), set(), set()

    def visit(key, delivery=False):
        if key not in records:
            return
        if delivery:
            closure.add(key)
        if key in active:
            errors.append(f"Dependency cycle at {key}")
            return
        mark = (key, delivery)
        if mark in visited:
            return
        active.add(key)
        deps = records[key].get("depends_on", [])
        if isinstance(deps, list):
            for dep in deps:
                if isinstance(dep, str):
                    visit(dep, delivery)
        active.remove(key)
        visited.add(mark)

    for key in records:
        visit(key)
    for key in selected:
        if not isinstance(key, str) or key not in records:
            errors.append(f"Unknown deliverable: {key}")
        else:
            visit(key, True)
    for key in sorted(closure):
        selected_issues.extend(f"{key}: {problem}" for problem in issues[key])
    return {
        "title": data.get("title"),
        "record_checks_passed": bool(selected) and not errors and not selected_issues,
        "notice": "Checks records and file hashes only; does not verify media quality or truth of review notes.",
        "errors": sorted(set(errors)),
        "delivery_issues": selected_issues,
        "action_issues": {key: value for key, value in issues.items() if value},
        "selected_deliverables": selected,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("directory", type=Path)
    init.add_argument("--title", required=True)
    init.add_argument("--mode", choices=["static-comic", "motion-comic", "live-action"], required=True)
    status = sub.add_parser("status")
    status.add_argument("directory", type=Path)
    args = parser.parse_args()
    root = args.directory.resolve()
    try:
        if args.command == "init":
            root.mkdir(parents=True, exist_ok=True)
            data = {"schema_version": 1, "title": args.title, "mode": args.mode,
                    "language": None, "aspect_ratio": None, "duration_range_seconds": None,
                    "tools": {"image": {"provider": "codex_builtin_image_gen", "status": "runtime_check_required"},
                              "video": {"provider": None, "status": "pending_user_integration"}},
                    "actions": [], "deliverables": []}
            with (root / "project.json").open("x", encoding="utf-8") as stream:
                json.dump(data, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            print(json.dumps({"created": str(root / "project.json"), "media_submitted": False}, ensure_ascii=False))
            return 0
        result = inspect(root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["record_checks_passed"] else 2
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
