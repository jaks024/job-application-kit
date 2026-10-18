# Browser operation and recovery

Use the supported browser tool's current documentation. This runbook describes
observed failure patterns, not fixed selectors or guaranteed site behavior.
Never use hidden APIs, cookie extraction, direct credential replay, or another
tool to evade an access restriction or required handoff.

## Session and identity

Select the user's requested browser and profile. Confirm candidate identity
before profile-based flows such as LinkedIn Easy Apply. A helper's account is
not the candidate's account. If identity differs, use the exact employer's
external application or hand off. Never silently switch browser profiles.

The main agent owns browser actions. A reviewer reads captured details and
returns findings. Keep user tabs open where work must resume. Do not close
unrelated tabs or reopen already-submitted forms.

## Common platform patterns

| Platform | What to check |
| --- | --- |
| Workday | Resume parsing often omits jobs, merges repeated employers, or treats projects as employment. Check all jobs and schools after parsing and on final review. |
| Greenhouse | Embedded uploads and email verification can expire. Check visible attachment retention; preserve the user's final-submit preference. |
| Lever / Ashby | Select the actual location suggestion. Autofill and attachment controls may be different. Parsing can insert a former employer as current. |
| Oracle | A prior resume may be reused. Check the current version and wait for saved history cards before adding another. |
| SuccessFactors / UKG | Visible text may not be committed. Use the tool's supported typing/Tab or suggestion selection, save, and inspect persisted values. |
| iCIMS | Profile creation, EEO, and application submission are separate stages. Account creation is not a job receipt. |
| Phenom / employer wrappers | A front-end upload may still require an ATS account step. Verify the final requisition status. |

## Bounded recovery

1. Inspect current visible state after a failure. A timeout can occur after a
   successful action. Do not repeat typing, uploading, or submitting blindly.
2. For uploads, use the documented file chooser and visible upload button. If an
   embedded frame blocks the control, only use its actually observed official
   source URL when supported and appropriate. Save answers before navigation.
3. If another supported route also fails, preserve the form and ask the user to
   attach the exact reviewed PDF. Never call a timed-out upload successful.
4. For missing-field validation, inspect a screenshot if contact fields are masked.
   Correct only the named field. Select real options and verify after save.
5. Match the displayed date format, including two- versus four-digit years.
   Dates visible before save can still be rejected or shifted by the server.
6. Refresh a failing session only after preserving answers and checking whether
   submission already succeeded. Refill and review the current version after reset.
7. After two evidence-based unsuccessful approaches, record the blocker and next
   step. Continue other authorized applications. Do not loop through reloads or
   create duplicate accounts/applications to test the site.

If an optional resume upload is broken, proceed without it only when the user
authorizes that choice and the required history is complete. Record the omission.
If a portal limits history entries, record the limit and obtain review before
certifying completeness. A resume attachment does not silently override a form's
explicit request for complete history.

## Referrals and verification

Start from the exact referral URL. Keep it privately, including its parameters.
Record any visible referral-source field or portal confirmation. Do not promise
referral attribution based only on the initial URL surviving sign-in.

Do not store OTPs, passwords, recovery codes, or identity-verification images.
The applicant handles sensitive identity checks where required. If verification
is unfinished, record a handoff rather than an application success.
