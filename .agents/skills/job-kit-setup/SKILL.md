---
name: job-kit-setup
description: Collect and confirm a candidate's information and configure a private Job Application Kit workspace. Use for first-time setup or updating a candidate profile and workflow preferences.
---

# Set up Job Application Kit

Resolve the kit root three directories above this skill. Read its `AGENTS.md`,
[setup guide](../../../docs/setup.md), and [data format](../../../docs/data-format.md).
Do not substitute another project's paths, profile, or tracker.

Create a new external private workspace with `tools/jobkit.py init` if needed.
Read existing private records before asking questions. Collect facts from the
user's documents, ask only material missing questions in small groups, and
confirm the summary. Separate unknowns from preferences and verified facts.
Never copy examples into the candidate profile as facts.

Configure broad role/geography/source coverage, internship constraints,
sponsorship policy, browser identity, resume review, submit preferences, and
optional tracker destination. Do not assume a specific nationality, authorization,
degree, experience count, pay floor, or location. Collect sensitive screening
facts only when needed; never collect credentials or identity-document numbers.

Review the approved master under [applications](../../../docs/applications.md),
align exact employment bullets, register it, and run `doctor`. Report confirmed
setup, unknowns, and next commands. Setup alone does not start applications,
employer messages, or recurring runs.
