# Private data format

All JSON uses UTF-8. Templates are blank scaffolds, not candidate facts. Paths in
records refer to the private workspace. The CLI refuses record-file paths that
resolve outside it. Do not put passwords, cookies, OTPs, document numbers, or
government-ID images in any record.

## Profile

`identity`, `availability`, `education`, `employment`, `projects`, `skills`,
`authorization`, `screening_answers`, `references`, and `motivation_notes` are
separate collections. Use `null` or `unknowns` for missing facts, never guessed defaults.

Each employment entry needs:

```json
{
  "id": "employment-1",
  "employer": "Example Company",
  "official_title": null,
  "resume_title": "Example Role",
  "location": null,
  "start_date": "2023-06",
  "end_date": "2024-08",
  "current": false,
  "bullets": ["A confirmed achievement copied exactly from the reviewed resume."],
  "source": "inputs/resume-source.txt",
  "confirmed_at": null
}
```

Use distinct IDs for two roles at one employer. Dates may be YYYY-MM or YYYY-MM-DD
depending on known precision. Do not invent a day for a month-only date; if a
form requires one, ask or record a candidate-approved convention.

Education entries contain `id`, `school`, `degree`, `subject`, `start_date`,
`end_date`, `completion_status`, optional `gpa` and `gpa_scale`, and `source`.
Projects contain their type (academic, research, personal), verified methods,
software, contribution, findings, dates, and source. Skills contain `name`,
`evidence`, and `confirmed_at`.

Authorization entries contain `country`, `status_description`, `authorized_now`,
`authorized_from`, `authorized_until`, `permanent_authorization`,
`requires_sponsorship_now`, `requires_sponsorship_later`, `conditions`, and `source`.
Use null for unknown booleans. These fields are facts for interpreting a question,
not a legal determination or a universal answer to differently worded forms.

Screening answers contain `question`, `answer`, `scope`, `confirmed_at`, and
`source`. Scope can limit an answer to an employer, country, time period, or exact
question. A reference or demographic answer must be explicitly supplied.

## Configuration

`templates/config.json` documents the supported workflow settings. Most are
read by the agent, not enforced by a browser bot. Arrays start empty. `preferred`
locations affect ranking; `required` locations exclude other places. Pay needs
amount, currency, and hourly/annual basis. Configure remote eligibility separately.

Use an IANA timezone, for example `Europe/London` or `America/Chicago`. The CLI
uses it for daily counts. Python on Windows may need the optional `tzdata` package.

`application.final_submit` is `user` or `agent_when_authorized`.
`platform_submit_overrides` can map a platform to either mode. This is a workflow
preference; it cannot override tool-required confirmation or a later user instruction.

## Job and event commands

Copy the job/event templates into the private workspace and fill them with
verified data. Leave the public templates unchanged.

```sh
python tools/jobkit.py add-job --file applications/example/job.json
python tools/jobkit.py record --file applications/example/event.json
python tools/jobkit.py status --date 2030-01-01
python tools/jobkit.py export
```

`add-job` returns the job key. If available, supply all three of `provider`,
`tenant` (employer board identifier), and `requisition_id`. This prevents one
platform's repeated numeric IDs from colliding across employers. Otherwise the
key is based on a canonical URL. Cross-source identity resolution remains an
operator task; do not create a second key for an already-known requisition.

The CLI removes only `utm_*`, `gclid`, and `fbclid` from canonical URLs. It preserves
unknown parameters and the original private URL. Do not publish referral URLs.

Every event uses a unique UUID and an ISO timestamp with offset. Evidence types:

| Type | Meaning |
| --- | --- |
| `portal_confirmation` | Employer explicitly confirmed the outcome |
| `user_confirmation` | User explicitly reported successful completion |
| `operator_note` | Preparation, blocker, review, or observed intermediate state |
| `user_directed_assumption` | User asked to treat it as done without confirmation; excluded from submission totals |

`resume_sha256` must identify an archived version or be null. Explain why null
when the portal accepted no resume. Store `review_file` and attachment evidence
privately. Hash validation proves the local artifact, not the employer's remote file.
`tracker_sync` and separate sync receipts record pending/verified external writes.

## Coverage cells

```json
{
  "name": "Core roles, recent window",
  "source": "employer careers",
  "query": "user-configured role family",
  "geography": "user-configured acceptable locations",
  "window": "preceding 24 hours",
  "state": "complete",
  "pages_checked": 2,
  "unique_leads": 3,
  "reason": "Available results exhausted",
  "next_step": null
}
```

This is a fictional format example, not evidence that a search ran. Preserve
query details, pagination stop reasons, blockers, and timestamps from the real run.
