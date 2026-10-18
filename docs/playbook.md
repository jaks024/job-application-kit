# Shared playbook

## Facts and permissions

1. Load the selected external workspace's `config.json` and `profile.json`.
   Confirm that the candidate and browser account are the intended person.
2. Keep facts, preferences, and permissions separate. A request to search does
   not authorize an application, account creation, employer email, or scheduling.
3. Reuse confirmed answers within their recorded scope. Missing facts stay
   unknown. Absence from a resume is not evidence of no criminal history,
   disability, relationships, licenses, prior applications, or employment.
4. Work authorization is country-, date-, and wording-specific. Record ordinary
   authorization, permanent authorization, sponsorship now, sponsorship later,
   and authorization dates separately. A possible extension is not an approval.
   Never supply a universal Yes/No default or change facts to pass a screen.
5. Do not put authorization details into motivation answers unless asked.
   Availability belongs in availability fields. Do not invent achievements,
   statistical tests, project stories, references, phone numbers, or credentials.
6. Preserve the user's current scope: excluded employers, referral holds,
   internship pay/location limits, and final-submit preferences. These are
   configuration, not defaults inherited from another candidate.
7. Apply tool-specific consent and credential rules at the relevant step. Do
   not create another tool, extension, or HTTP path to evade a blocked action.

## Ownership

The main session operates the browser, submits when authorized, saves receipts,
and updates the tracker. If the user requests delegation, a second agent checks
upcoming postings, prepares supported answers, and reviews captured form details.
It must not control tabs, submit, or write the tracker. Pass only relevant facts.
Use inherited model settings unless the user specifies otherwise. Report when
review was done by the operator rather than an independent agent.

Research can be split by non-overlapping public sources when delegation is
authorized. Workers return evidence and gaps. The main session merges records
and owns all shared writes. A tool failure must not cause competing browser owners.

## Canonical artifacts

- The confirmed profile is the fact source; each factual addition has provenance.
- A reviewed master PDF is reused unchanged unless a useful, supported skills
  change is needed or the user asks to revise the experience content.
- Keep academic projects separate from employment, and future work separate
  from completed work. A resume title is not automatically an official payroll title.
- Archive each submitted resume version, posting, form review, and receipt.
  Never alter submitted evidence when the master changes.
- Only provide cover letters when required or requested.

## Completion

Search ends when the declared broad coverage is completed or specific access
gaps are recorded. It is not complete merely because a few good jobs were found.
Application work ends at a verified outcome or a named handoff. A click, a
disappearing tab, an account, or a saved profile is not a submission receipt.

Record every outcome locally before tracker synchronization. Preserve confirmed
submissions during later search refreshes. Report user-confirmed submissions,
portal-confirmed submissions, uncertain attempts, skips, and handoffs distinctly.
Do not count an instruction to “assume done” as submission confirmation.
