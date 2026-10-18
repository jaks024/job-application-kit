#!/usr/bin/env python3
"""Local records for an agent-assisted search. No browser or employer API calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import sys
import uuid
from datetime import date, datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parents[1]
STATES = ("New", "Prepared", "Awaiting user", "Blocked", "Submission uncertain",
          "Applied", "Interview", "Offer", "Rejected", "Withdrawn", "Skipped", "Handed off")
POST_SUBMISSION = {"Applied", "Interview", "Offer", "Rejected", "Withdrawn"}
EVIDENCE = {"portal_confirmation", "user_confirmation", "operator_note", "user_directed_assumption"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def external_path(path):
    resolved = Path(path).expanduser().resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError("Candidate workspaces must be outside the kit repository.")
    if any((p / ".git").exists() for p in [resolved, *resolved.parents]):
        raise ValueError("Candidate workspaces must not be inside a Git checkout.")
    return resolved


def workspace(value=None):
    if value is None:
        pointer = ROOT / ".jobkit-workspace"
        if not pointer.exists():
            raise ValueError("Pass --workspace or run init first.")
        value = pointer.read_text(encoding="utf-8").strip()
    path = external_path(value)
    if not (path / ".jobkit-private").is_file():
        raise ValueError("Not an initialized private workspace.")
    return path


def private_file(ws, name):
    path = (ws / name).resolve()
    if path == ws or ws not in path.parents:
        raise ValueError("Record files must stay inside the selected private workspace.")
    return path


def connection(ws):
    # Validate the file path as well as its parent to reject symlink escapes.
    db = private_file(ws, "tracker.sqlite3")
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_key TEXT PRIMARY KEY, company TEXT NOT NULL, role TEXT NOT NULL,
            canonical_url TEXT NOT NULL, details TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'New',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY, job_key TEXT NOT NULL REFERENCES jobs(job_key),
            occurred_at TEXT NOT NULL, local_date TEXT NOT NULL, state TEXT NOT NULL,
            evidence_type TEXT NOT NULL, payload TEXT NOT NULL
        );
    """)
    return conn


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def canonical_url(value):
    url = urlsplit(value)
    if url.scheme not in {"https", "http"} or not url.hostname or url.username or url.password:
        raise ValueError("Use an http(s) posting URL without embedded credentials.")
    # Preserve requisition and referral parameters. Never guess that an unknown parameter is tracking.
    query = [(k, v) for k, v in parse_qsl(url.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in {"gclid", "fbclid"}]
    return urlunsplit((url.scheme.lower(), url.netloc.lower(), url.path or "/", urlencode(query), url.fragment))


def key_for(job):
    url = canonical_url(job["url"])
    parts = [job.get(k) for k in ("provider", "tenant", "requisition_id")]
    if all(isinstance(x, str) and x.strip() for x in parts):
        # JSON encoding is unambiguous even if a tenant or requisition contains a separator.
        identity = json.dumps([parts[0].strip().lower(), parts[1].strip().lower(), parts[2].strip()])
        return "id-" + hashlib.sha256(identity.encode()).hexdigest()[:24], url
    return "url-" + hashlib.sha256(url.encode()).hexdigest()[:24], url


def init(args):
    ws = external_path(args.workspace)
    if ws.exists():
        raise ValueError("Choose a new directory. init never replaces an existing workspace.")
    ws.mkdir(parents=True)
    (ws / ".jobkit-private").write_text("Private candidate workspace. Never publish.\n", encoding="utf-8")
    (ws / ".gitignore").write_text("*\n", encoding="utf-8")
    (ws / "AGENTS.md").write_text(
        "# Private candidate workspace\nNever initialize Git, publish this folder, or store passwords, "
        "session tokens, identity-document numbers or OTPs here. Use the Job Application Kit playbook. "
        "Unknown facts remain unknown. Confirm the candidate and target account before external actions.\n",
        encoding="utf-8")
    for name in ("config", "profile"):
        write_json(ws / (name + ".json"), read_json(ROOT / "templates" / (name + ".json")))
    for name in ("inputs", "resumes", "applications", "runs", "interviews"):
        (ws / name).mkdir()
    with connection(ws):
        pass
    (ROOT / ".jobkit-workspace").write_text(str(ws) + "\n", encoding="utf-8")
    return {"workspace": str(ws), "next": "Use $job-kit-setup to fill and confirm config.json and profile.json."}


def doctor(args):
    ws = workspace(args.workspace)
    config, profile = read_json(ws / "config.json"), read_json(ws / "profile.json")
    issues = []
    timezone = config.get("timezone")
    try:
        ZoneInfo(timezone or "")
    except (ValueError, ZoneInfoNotFoundError):
        issues.append("Set a valid IANA timezone. On Windows, install tzdata if unavailable.")
    for field in ("role_families", "countries", "job_types", "sources"):
        if not config.get("search", {}).get(field):
            issues.append("Missing search." + field)
    if not profile.get("confirmed_at"):
        issues.append("Candidate profile is not yet confirmed.")
    for field in ("legal_name", "email"):
        if not profile.get("identity", {}).get(field):
            issues.append("Missing identity." + field)
    if not (ws / "resumes" / "master.json").exists():
        issues.append("No reviewed master resume registered; discovery can still run.")
    else:
        try:
            check_master(ws)
        except (ValueError, OSError) as exc:
            issues.append(str(exc))
    print(json.dumps({"ready": not issues, "issues": issues}, indent=2))
    return 1 if issues else 0


def roles(ws, sha):
    result = []
    seen = set()
    for entry in read_json(ws / "profile.json")["employment"]:
        required = ("id", "employer", "resume_title", "start_date", "bullets")
        if any(not entry.get(k) for k in required) or "end_date" not in entry:
            raise ValueError("Each employment record needs id, employer, resume_title, dates and bullets.")
        if entry["id"] in seen:
            raise ValueError("Employment IDs must be unique, including repeat employers.")
        seen.add(entry["id"])
        bullets = entry["bullets"]
        if not isinstance(bullets, list) or any(not isinstance(b, str) or not b.strip() or "\n" in b or "\r" in b or b.startswith(("- ", "•")) for b in bullets):
            raise ValueError("Each bullet must be one logical plain-text line without a bullet marker.")
        result.append({"id": entry["id"], "employer": entry["employer"],
                       "title": entry["resume_title"], "start_date": entry["start_date"],
                       "end_date": entry["end_date"], "description": "\n".join("- " + b for b in bullets)})
    return {"pdf_sha256": sha, "employment": result}


def register_resume(args):
    ws = workspace(args.workspace)
    if not args.reviewed:
        raise ValueError("Render, inspect, extract text, and compare facts before passing --reviewed.")
    pdf = private_file(ws, args.pdf)
    if pdf.suffix.lower() != ".pdf" or not pdf.read_bytes().startswith(b"%PDF-"):
        raise ValueError("Expected an actual PDF inside the private workspace.")
    sha = digest(pdf)
    role_data = roles(ws, sha)
    if args.variant:
        check_master(ws)
    destination = private_file(ws, "resumes/versions/" + sha + "/Resume.pdf")
    destination.parent.mkdir(parents=True, exist_ok=True)
    role_path = destination.parent / "role-descriptions.json"
    if role_path.exists() and read_json(role_path) != role_data:
        raise ValueError("This PDF hash has a different archived role map. Reconcile the PDF and profile; do not overwrite history.")
    if not destination.exists():
        shutil.copyfile(pdf, destination)
    manifest = {"sha256": sha, "pdf": destination.relative_to(ws).as_posix(),
                "reviewed_at": now(), "review_note": args.review_note}
    write_json(role_path, role_data)
    if args.variant:
        write_json(destination.parent / "review.json", manifest)
    else:
        write_json(ws / "resumes/master.json", manifest)
    return manifest


def check_master(ws):
    manifest = read_json(ws / "resumes/master.json")
    pdf = private_file(ws, manifest["pdf"])
    if digest(pdf) != manifest["sha256"]:
        raise ValueError("Registered master PDF changed. Review and register the new version.")
    stored_roles = read_json(pdf.parent / "role-descriptions.json")
    if stored_roles != roles(ws, manifest["sha256"]):
        raise ValueError("Employment facts or bullets changed. Reconcile the master and re-register after review.")
    return manifest


def add_job(args):
    ws = workspace(args.workspace)
    job = read_json(private_file(ws, args.file))
    for field in ("company", "role", "url"):
        if not isinstance(job.get(field), str) or not job[field].strip():
            raise ValueError("Job requires " + field)
    key, url = key_for(job)
    with connection(ws) as db:
        existing = db.execute("SELECT * FROM jobs WHERE job_key=?", (key,)).fetchone()
        if existing:
            if existing["company"].casefold() != job["company"].casefold():
                raise ValueError("Identity collision: inspect provider, tenant, requisition and company.")
            details = json.loads(existing["details"])
            details.update({k: v for k, v in job.items() if v not in (None, "", [], {})})
            db.execute("UPDATE jobs SET role=?, details=?, updated_at=? WHERE job_key=?",
                       (job["role"], json.dumps(details), now(), key))
        else:
            db.execute("INSERT INTO jobs VALUES (?,?,?,?,?,'New',?,?)",
                       (key, job["company"], job["role"], url, json.dumps(job), now(), now()))
    return {"job_key": key, "existing": bool(existing), "state": existing["state"] if existing else "New"}


def record(args):
    ws = workspace(args.workspace)
    event = read_json(private_file(ws, args.file))
    for name in ("event_id", "job_key", "state", "occurred_at", "evidence_type", "evidence"):
        if not isinstance(event.get(name), str) or not event[name].strip():
            raise ValueError("Event requires nonempty " + name)
    uuid.UUID(event["event_id"])
    if event["state"] not in STATES or event["evidence_type"] not in EVIDENCE:
        raise ValueError("Unknown state or evidence type. See docs/data-format.md.")
    stamp = datetime.fromisoformat(event["occurred_at"])
    if stamp.utcoffset() is None:
        raise ValueError("occurred_at must include a timezone offset.")
    zone = ZoneInfo(read_json(ws / "config.json")["timezone"])
    local_date = stamp.astimezone(zone).date().isoformat()
    if event["state"] == "Applied" and event["evidence_type"] not in {"portal_confirmation", "user_confirmation"}:
        raise ValueError("Applied requires portal or explicit user confirmation; use Handed off or Submission uncertain otherwise.")
    sha = event.get("resume_sha256")
    if sha is not None and not re.fullmatch(r"[a-f0-9]{64}", sha):
        raise ValueError("resume_sha256 must be a SHA-256 hex digest or null.")
    if sha:
        archive = private_file(ws, "resumes/versions/" + sha + "/Resume.pdf")
        if not archive.is_file() or digest(archive) != sha:
            raise ValueError("The event's resume hash has no matching archived PDF.")
    payload = json.dumps(event, sort_keys=True)
    with connection(ws) as db:
        previous = db.execute("SELECT payload FROM events WHERE event_id=?", (event["event_id"],)).fetchone()
        if previous:
            if previous["payload"] != payload:
                raise ValueError("That event_id already has different content; do not overwrite evidence.")
            return {"recorded": True, "duplicate": True, "event_id": event["event_id"]}
        job = db.execute("SELECT state FROM jobs WHERE job_key=?", (event["job_key"],)).fetchone()
        if not job:
            raise ValueError("Unknown job key. Add the job first.")
        state = event["state"]
        if job["state"] in POST_SUBMISSION and (state not in POST_SUBMISSION or state == "Applied"):
            state = job["state"]
        db.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?)", (event["event_id"], event["job_key"],
                   stamp.isoformat(), local_date, event["state"], event["evidence_type"], payload))
        db.execute("UPDATE jobs SET state=?, updated_at=? WHERE job_key=?", (state, now(), event["job_key"]))
    return {"recorded": True, "event_id": event["event_id"], "current_state": state}


def report(args):
    ws = workspace(args.workspace)
    if args.date is not None:
        date.fromisoformat(args.date)
    with connection(ws) as db:
        jobs = [dict(r) for r in db.execute("SELECT job_key, company, role, state FROM jobs ORDER BY company, role")]
        # One submission per requisition, on its first confirmed application date.
        all_events = [dict(r) for r in db.execute("SELECT * FROM events ORDER BY julianday(occurred_at), event_id")]
    first = {}
    for event in all_events:
        if event["state"] == "Applied" and event["job_key"] not in first:
            first[event["job_key"]] = event
    chosen = [e for e in first.values() if args.date is None or e["local_date"] == args.date]
    return {"date": args.date, "confirmed_submissions": len(chosen),
            "portal_confirmed": sum(e["evidence_type"] == "portal_confirmation" for e in chosen),
            "user_confirmed": sum(e["evidence_type"] == "user_confirmation" for e in chosen),
            "jobs": jobs}


def export(args):
    ws = workspace(args.workspace)
    with connection(ws) as db:
        jobs = [dict(r) for r in db.execute("SELECT * FROM jobs ORDER BY job_key")]
        events = [json.loads(r["payload"]) for r in db.execute("SELECT payload FROM events ORDER BY occurred_at")]
    for job in jobs:
        job["details"] = json.loads(job["details"])
    output = private_file(ws, args.output)
    write_json(output, {"exported_at": now(), "jobs": jobs, "events": events})
    return {"path": str(output), "jobs": len(jobs), "events": len(events)}


def coverage(args):
    ws = workspace(args.workspace)
    data = read_json(private_file(ws, args.file))
    cells = data.get("cells", [])
    gaps = []
    if not cells:
        gaps.append("No search cells declared.")
    for i, cell in enumerate(cells):
        for field in ("name", "source", "query", "geography", "window", "state"):
            if not cell.get(field):
                gaps.append(f"Cell {i}: missing {field}")
        if cell.get("state") not in {"complete", "blocked", "not_applicable"}:
            gaps.append(f"Cell {i}: accessible work remains")
        if not cell.get("reason"):
            gaps.append(f"Cell {i}: missing stop reason")
        if cell.get("state") == "blocked" and not cell.get("next_step"):
            gaps.append(f"Cell {i}: missing blocked-source next step")
    print(json.dumps({"ledger_closed": not gaps, "gaps": gaps,
                      "blocked_cells": sum(c.get("state") == "blocked" for c in cells),
                      "note": "Closure does not prove full market coverage or correct cell selection."}, indent=2))
    return 1 if gaps else 0


def install_skills(args):
    destination = Path(args.destination).expanduser().resolve()
    sources = sorted((ROOT / ".agents/skills").glob("*/SKILL.md"))
    if any((destination / p.parent.name).exists() for p in sources):
        raise ValueError("One or more skills already exist. No files written; review existing skills manually.")
    for source in sources:
        target = destination / source.parent.name
        target.mkdir(parents=True)
        frontmatter = source.read_text(encoding="utf-8").split("---", 2)[1]
        (target / "SKILL.md").write_text("---" + frontmatter + "---\n\nRead and follow the canonical skill at [SKILL.md](" + source.as_posix() + "). Resolve its references from that directory. Do not assume the caller's working directory is the kit.\n", encoding="utf-8")
    return {"installed": len(sources), "destination": str(destination), "note": "Wrappers point to this clone; keep it in place."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "doctor", "register-resume", "check-resume", "add-job", "record", "status", "export", "coverage"):
        p = sub.add_parser(name)
        p.add_argument("--workspace", required=name == "init")
        if name in {"add-job", "record", "coverage"}:
            p.add_argument("--file", required=True, help="JSON file inside the private workspace")
        if name == "register-resume":
            p.add_argument("--pdf", required=True)
            p.add_argument("--reviewed", action="store_true")
            p.add_argument("--review-note", required=True)
            p.add_argument("--variant", action="store_true", help="Archive a reviewed variant without replacing the master")
        if name == "status":
            p.add_argument("--date", help="Candidate-local YYYY-MM-DD; otherwise all-time")
        if name == "export":
            p.add_argument("--output", default="tracker-export.json")
    p = sub.add_parser("install-skills")
    p.add_argument("--destination", required=True)
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            return doctor(args)
        if args.command == "coverage":
            return coverage(args)
        actions = {"init": init, "register-resume": register_resume, "add-job": add_job,
                   "record": record, "status": report, "export": export, "install-skills": install_skills}
        result = check_master(workspace(args.workspace)) if args.command == "check-resume" else actions[args.command](args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, sqlite3.Error, ZoneInfoNotFoundError) as exc:
        print("Error: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
