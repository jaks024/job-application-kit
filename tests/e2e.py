#!/usr/bin/env python3
"""E2E: exercise real CLI, SQLite, file archives, skills, and Git privacy boundaries."""
import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run(*args, cwd=None, expected=0):
    result = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == expected, f"Command failed: {args}\n{result.stdout}\n{result.stderr}"
    return result.stdout


def simple_pdf():
    # A real one-page PDF with a readable synthetic text layer; no candidate data.
    stream = b"BT /F1 12 Tf 72 720 Td (Example Candidate Resume) Tj ET"
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
               b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"]
    content = b"%PDF-1.4\n"
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(content))
        content += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    start = len(content)
    content += b"xref\n0 6\n0000000000 65535 f \n"
    content += b"".join(f"{n:010d} 00000 n \n".encode() for n in offsets[1:])
    return content + f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n".encode()


def main():
    with tempfile.TemporaryDirectory(prefix="jobkit-e2e-") as temporary:
        base = Path(temporary)
        kit = base / "kit"
        allowed = json.loads((ROOT / "public-files.json").read_text(encoding="utf-8"))
        for name in allowed:
            dest = kit / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        cli = kit / "tools/jobkit.py"
        scan = kit / "tools/privacy_scan.py"
        ws = base / "candidate-private"

        def command(*args, expected=0):
            return run(sys.executable, cli, *args, expected=expected)

        command("init", "--workspace", kit / "unsafe", expected=1)
        command("init", "--workspace", ws)
        command("init", "--workspace", ws, expected=1)
        command("doctor", expected=1)
        config = json.loads((ws / "config.json").read_text())
        config["timezone"] = "America/Chicago"
        config["search"].update(role_families=["Research"], countries=["US"], job_types=["Full-time"], sources=["employer"])
        write(ws / "config.json", config)
        profile = json.loads((ws / "profile.json").read_text())
        profile["identity"].update(legal_name="Example Candidate", email="candidate@example.com")
        profile["confirmed_at"] = "2030-01-01"
        profile["employment"] = [
            {"id": "job-1", "employer": "Example Company", "resume_title": "Analyst",
             "start_date": "2024-01", "end_date": "2024-12", "bullets": ["Reviewed synthetic records.", "Presented findings."]},
            {"id": "job-2", "employer": "Example Company", "resume_title": "Intern",
             "start_date": "2023-06", "end_date": "2023-08", "bullets": ["Checked input quality."]}]
        write(ws / "profile.json", profile)
        pdf = ws / "inputs/Resume.pdf"
        pdf.write_bytes(simple_pdf())
        command("register-resume", "--pdf", "inputs/Resume.pdf", "--review-note", "Synthetic fixture", expected=1)
        registered = json.loads(command("register-resume", "--pdf", "inputs/Resume.pdf", "--reviewed", "--review-note", "Synthetic fixture reviewed"))
        frozen = ws / registered["pdf"]
        descriptions = json.loads((frozen.parent / "role-descriptions.json").read_text())
        assert len(descriptions["employment"]) == 2
        assert descriptions["employment"][0]["description"] == "- Reviewed synthetic records.\n- Presented findings."
        command("check-resume")
        command("doctor")

        # Source edits do not alter the archived PDF; profile changes invalidate its mapping.
        pdf.write_bytes(simple_pdf() + b"\n% altered source\n")
        command("check-resume")
        variant = json.loads(command("register-resume", "--pdf", "inputs/Resume.pdf", "--variant", "--reviewed", "--review-note", "Synthetic variant reviewed"))
        assert variant["sha256"] != registered["sha256"]
        assert json.loads(command("check-resume"))["sha256"] == registered["sha256"]
        profile["employment"][0]["bullets"].append("An unreviewed change.")
        write(ws / "profile.json", profile)
        command("check-resume", expected=1)
        profile["employment"][0]["bullets"].pop()
        write(ws / "profile.json", profile)

        job = {"provider": "example", "tenant": "employer-one", "requisition_id": "42",
               "company": "Example Company", "role": "Research Analyst", "url": "https://careers.example.com/jobs/42?utm_source=board&referral=keep"}
        job_file = ws / "applications/example/job.json"
        write(job_file, job)
        key = json.loads(command("add-job", "--file", job_file))["job_key"]
        assert json.loads(command("add-job", "--file", job_file))["existing"]
        job["tenant"] = "employer-two"
        job["company"] = "Second Example Company"
        write(ws / "applications/second/job.json", job)
        other = json.loads(command("add-job", "--file", "applications/second/job.json"))["job_key"]
        assert other != key
        command("add-job", "--file", "../outside.json", expected=1)

        event = {"event_id": str(uuid.uuid4()), "job_key": key, "state": "Applied",
                 "occurred_at": "2030-01-02T01:00:00+00:00", "evidence_type": "operator_note",
                 "evidence": "Not yet confirmed", "resume_sha256": registered["sha256"]}
        event_file = ws / "applications/example/event.json"
        write(event_file, event)
        command("record", "--file", event_file, expected=1)
        event.update(evidence_type="portal_confirmation", evidence="Synthetic portal success")
        write(event_file, event)
        command("record", "--file", event_file)
        assert json.loads(command("record", "--file", event_file))["duplicate"]
        event["evidence"] = "Changed payload"
        write(event_file, event)
        command("record", "--file", event_file, expected=1)
        event.update(event_id=str(uuid.uuid4()), state="Interview", evidence_type="user_confirmation")
        write(event_file, event)
        command("record", "--file", event_file)
        event.update(event_id=str(uuid.uuid4()), state="Prepared", evidence_type="operator_note")
        write(event_file, event)
        assert json.loads(command("record", "--file", event_file))["current_state"] == "Interview"
        command("add-job", "--file", job_file)
        summary = json.loads(command("status", "--date", "2030-01-01"))
        assert summary["confirmed_submissions"] == 1 and summary["portal_confirmed"] == 1
        assert json.loads(command("status", "--date", "2030-01-02"))["confirmed_submissions"] == 0
        event.update(event_id=str(uuid.uuid4()), job_key=other, state="Handed off", evidence_type="user_directed_assumption")
        write(event_file, event)
        command("record", "--file", event_file)
        assert json.loads(command("status"))["confirmed_submissions"] == 1
        command("export")
        exported = json.loads((ws / "tracker-export.json").read_text())
        assert exported["jobs"][0]["canonical_url"].endswith("?referral=keep")
        command("export", "--output", "../../escape.json", expected=1)
        command("install-skills", "--destination", base / "skills")
        command("install-skills", "--destination", base / "skills", expected=1)
        assert len(list((base / "skills").glob("*/SKILL.md"))) == 4

        coverage_file = ws / "runs/synthetic/coverage.json"
        write(coverage_file, {"cells": [{"name": "test", "state": "pending"}]})
        command("coverage", "--file", coverage_file, expected=1)
        write(coverage_file, {"cells": [{"name": "test", "source": "employer", "query": "research", "geography": "configured", "window": "recent", "state": "blocked", "reason": "connection unavailable", "next_step": "reconnect"}]})
        command("coverage", "--file", coverage_file)

        run(sys.executable, scan)
        leak = kit / "private-note.txt"
        leak.write_text("candidate" + "@" + "private.invalid", encoding="utf-8")
        flagged = json.loads(run(sys.executable, scan, expected=1))
        assert any("personal_email" in f["categories"] for f in flagged["findings"])
        leak.unlink()

        # Real Git index/history checks must still catch a private value after working-tree repair.
        run("git", "init", "--initial-branch=main", kit)
        run("git", "config", "user.name", "Example Maintainer", cwd=kit)
        run("git", "config", "user.email", "maintainer@example.com", cwd=kit)
        run("git", "add", "--", *allowed, cwd=kit)
        run(sys.executable, scan, "--mode", "index")
        original = (kit / "README.md").read_text(encoding="utf-8")
        (kit / "README.md").write_text(original + "\ncandidate" + "@" + "private.invalid\n", encoding="utf-8")
        run("git", "add", "README.md", cwd=kit)
        (kit / "README.md").write_text(original, encoding="utf-8")
        run(sys.executable, scan, "--mode", "index", expected=1)
        run("git", "commit", "-m", "Synthetic privacy regression fixture", cwd=kit)
        run("git", "add", "README.md", cwd=kit)
        run("git", "commit", "-m", "Remove synthetic fixture", cwd=kit)
        run(sys.executable, scan, "--mode", "index")
        run(sys.executable, scan, "--mode", "history", expected=1)
        command("init", "--workspace", kit / "nested-private", expected=1)

    evidence = ROOT / ".artifacts/e2e/report.json"
    write(evidence, {"passed": True, "checks": ["external workspace boundaries", "resume archive and role export",
          "real SQLite identity and events", "timezone totals", "nonregressing state", "idempotent receipts",
          "coverage gaps", "skill wrapper install", "working tree, Git index and history leak detection"]})
    print("E2E passed. Synthetic data only. Report: .artifacts/e2e/report.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
