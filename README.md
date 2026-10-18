# Job Application Kit

An agent-assisted workflow for finding jobs, preparing applications, checking
forms, and recording outcomes. Bring your own resume, candidate facts, AI agent,
and supported browser connection. Personal data stays in a separate local workspace.

## What it does

- Guided onboarding with reusable skills and a confirmed candidate profile.
- Broad search on the first pass: core and adjacent roles, different industries,
  preferred and acceptable locations, recent openings, overlooked jobs, and
  internships when enabled.
- A reviewed master resume, optional skills-only variants, version hashes, and
  exact `- ` bullet lists for application forms.
- Browser runbooks for incomplete resume parsing, failed uploads, expired forms,
  referral links, and uncertain submissions.
- Local SQLite tracking, evidence-backed submission counts, and optional Notion
  synchronization through your agent's connected tools.
- Interview preparation using the posting and resume that were actually submitted.

**This is not an unattended application bot.** The Python tools manage local
records. Your agent uses its own web/browser tools to search and fill forms.
Accounts, MFA, CAPTCHA, consents, and submissions follow the connected tool's
rules and your selected review preferences. No browser extension, cookies,
credentials, hosted service, or Notion token is bundled.

## Quick start

1. Install Python 3.10+ and Git. Clone this repository:

   ```sh
   git clone https://github.com/jaks024/job-application-kit.git
   cd job-application-kit
   ```

2. Open this folder in your agent. Codex can discover `.agents/skills/`. Other
   agents can read `AGENTS.md` and the skill files directly. If you want Codex
   skills available from other folders, install local pointers:

   ```sh
   python tools/jobkit.py install-skills --destination ~/.codex/skills
   ```

   Keep this clone in place. The command refuses to overwrite existing skills.

3. Create a private workspace **outside every Git checkout**. For example:

   ```sh
   python tools/jobkit.py init --workspace ~/job-search-private
   ```

   The command creates blank profile/config files and a local tracker. It writes
   an ignored `.jobkit-workspace` pointer in this clone. Existing directories are
   never replaced. Use separate workspaces for separate people; pass
   `--workspace` to switch explicitly.

4. Ask your agent:

   > Use $job-kit-setup to collect my information and configure this workspace.
   > Ask me for missing facts in small groups. Review my resume before using it.

   Give it your resume file and search preferences. It will confirm identities,
   work history, education, authorization, availability, and workflow settings.
   It should collect sensitive screening details only when needed for a real form.

5. Connect a supported browser. Confirm the browser profile belongs to the
   candidate before using profile-based application services. Optionally connect
   Notion and choose the exact destination. Local tracking works without Notion.

6. Run a search, then authorize the applications you want:

   > Use $job-kit-search for today's broad search, including my enabled internships.

   > Use $job-kit-apply for these selected jobs with my reviewed master resume.
   > Use a second agent to review. Leave final submission to me.

7. Ask for interview preparation when needed:

   > Use $job-kit-interview for this recruiter call. Use the submitted resume and
   > posting, and research the interview process with dated sources.

On Windows, PowerShell accepts the same commands. Use `py` instead of `python`
if that is how Python is installed. Timezone support may require
`python -m pip install tzdata`. The core tools otherwise use the standard library.

## Resume setup

Use your own approved format. A blank LaTeX starter is in `templates/resume.tex`;
it is optional. Set the page target and page size for your field and country.
Compile locally with a trusted LaTeX installation, or export from your editor.
An editor preview is not proof that the PDF saved on disk is current.

For a text-layer check, install `pypdf` or Poppler:

```sh
python -m pip install pypdf
python tools/verify_pdf.py ~/job-search-private/inputs/Resume.pdf --pages 1 --dump-text ~/job-search-private/resumes/extracted.txt
```

Use your actual page target. Render and visually inspect the PDF as well. Then
align each employment record's bullets with it and register the approved version:

```sh
python tools/jobkit.py register-resume --pdf inputs/Resume.pdf --reviewed --review-note "Content, text extraction, and rendered pages reviewed."
python tools/jobkit.py check-resume
python tools/jobkit.py doctor
```

`--reviewed` records an assertion by the operator; it does not inspect the PDF
for you. Registration archives the PDF by hash and exports the role descriptions.
Add `--variant` for a reviewed skills-only copy without replacing the master.

## Documentation

| Guide | Purpose |
| --- | --- |
| [Setup](docs/setup.md) | Candidate intake, tools, and workspace choices |
| [Playbook](docs/playbook.md) | Shared rules and ownership |
| [Search](docs/search.md) | Coverage, verification, ranking, deduplication |
| [Applications](docs/applications.md) | Resume and form checks, review, submission |
| [Browser runbook](docs/browser.md) | Platform behavior and recovery |
| [Tracking](docs/tracking.md) | Receipts, daily totals, optional Notion sync |
| [Data format](docs/data-format.md) | Profile and CLI record contracts |
| [Interview preparation](docs/interviews.md) | Role-specific preparation |
| [Privacy and publishing](docs/privacy.md) | Keeping candidate data out of Git |

## Local tools

Run `python tools/jobkit.py --help` or a subcommand's `--help`.

| Command | Effect |
| --- | --- |
| `init --workspace PATH` | Create a blank external workspace |
| `doctor` | Find missing setup and stale resume records |
| `register-resume --pdf PATH --reviewed --review-note TEXT` | Freeze a reviewed PDF and role descriptions |
| `check-resume` | Check the archived master hash and employment mapping |
| `add-job --file PATH` | Insert or refresh a job without resetting its application state |
| `record --file PATH` | Append an evidence-backed application event |
| `status --date YYYY-MM-DD` | Count distinct confirmed submissions in candidate-local time |
| `export --output tracker-export.json` | Export private records for review or tracker sync |
| `coverage --file PATH` | Check a search ledger for unfinished cells |
| `install-skills --destination PATH` | Install pointers to this clone's skills |

All record paths are relative to the private workspace or absolute paths inside
it. These commands never submit applications, contact employers, or call Notion.
They do not encrypt files. Use your operating system's normal access controls
and encrypted storage if needed.

## Development and publication

Enable the optional local publication guards once per clone:

```sh
git config core.hooksPath .githooks
```

They scan the index before a commit and reachable history before a push. They
use `python` on PATH and do not replace manual review or a candidate denylist.

```sh
python tests/e2e.py
python tools/privacy_scan.py
python tools/privacy_scan.py --mode index
python tools/privacy_scan.py --mode history
```

Tests use synthetic data in temporary directories and make no network requests.
The publication scanner uses `public-files.json`, rejects unexpected files and
common private-data patterns, and can inspect staged content and Git history.
It cannot recognize all personal data; manually review every file and the index.
See [privacy.md](docs/privacy.md) before sharing a fork or a release.

MIT licensed. The PDF text verifier is adapted from
[MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search).
See [NOTICE.md](NOTICE.md) for attribution and scope.
