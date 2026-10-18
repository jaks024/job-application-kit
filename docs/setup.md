# Setup and intake

## 1. Establish the private workspace

Ask whose applications this is for and whether the user is helping someone else.
Choose an external folder and run `jobkit.py init`. Do not initialize Git in it.
Read existing records before asking questions; setup must not reset prior answers.
The ignored `.jobkit-workspace` file selects one workspace, while `--workspace`
always takes precedence. Confirm the selection when switching people.

## 2. Collect facts in small groups

Begin with the resume and search preferences. Extract a draft profile from the
documents, identify uncertain parsing, and ask the user to confirm corrections.
Do not ask for every possible screening answer during onboarding.

- Identity: legal/preferred name, application email, phone, location, links.
- Education: each school, degree, subject, dates, expected/completed status,
  and GPA only if supplied. Keep dates at their known precision.
- Employment: every separate role, including multiple roles at one employer;
  official and resume titles, location, dates, current status, exact bullets.
- Academic/research/personal projects in a separate collection.
- Confirmed skills and evidence; no keywords inferred from target postings.
- Availability, relocation, travel, working hours, accepted commitments.
- Work eligibility by country and time period; ask for facts rather than
  passwords, document numbers, or copies of sensitive identity documents.
- Standing screening answers only when supplied, with exact scope, confirmation
  date, and source. Ask material new facts when a real form requires them.
- References only with permission; collect actual details when needed.

Record each assertion's source, such as a private document path or dated user
confirmation. Record contradictory evidence and resolve it; do not silently
prefer whichever answer makes an application easier.

## 3. Configure search and application preferences

Collect role families and adjacent titles, industries, target countries,
preferred versus required geography, remote eligibility, job types, pay currency
and basis, internship dates/enrollment/pay/location rules, and exclusions.
Ask whether experience or enrollment mismatches should be included with flags.
Separate explicit no-sponsorship exclusions from unknown/ambiguous language.
An internship's temporary authorization does not answer a question about future
sponsorship; follow its exact wording.

Choose timezone, resume page target, cover-letter policy, final-submit mode,
platform-specific handoffs, reviewer preference, and optional contact preferences.
Demographic responses require the candidate's choice. Nondisclosure is available
only where the form offers it; do not infer a protected characteristic.

## 4. Connect tools

Use the agent's currently supported web/browser tools. Verify the requested
browser profile. A helper's LinkedIn account must not submit another person's
profile. Prefer the exact employer posting if the logged-in identity differs.
Do not extract browser cookies, profiles, passwords, or session tokens.

Notion is optional. If selected, ask for the exact database/page, fetch its
schema and complete roster, and save its IDs only in the private config.
Confirm who edits which fields. Setup does not authorize unrelated workspace
changes. Never choose a database from another project by default.

## 5. Review and freeze

Present a compact summary of confirmed facts, hard filters, preferences, and
unknowns. Obtain the user's corrections. Set `profile.confirmed_at` only after
confirmation. Review the real resume under [applications.md](applications.md),
register it, and run `doctor`. Search can start without a resume if the user
requests opportunity discovery; label personal fit as unassessed.

Do not start applying, messaging, or scheduling merely because setup is complete.
