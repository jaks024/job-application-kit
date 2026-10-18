# Application preparation and review

## Before opening a form

Confirm the exact job identity, availability, user scope, duplicate history, and
referral hold. Archive the source posting. Apply configured sponsorship and
internship exclusions. A search ranking is not permission to submit.

Run `check-resume`. Reuse the registered master PDF unchanged when appropriate.
Do not repeatedly rewrite the same achievements for cosmetic tailoring. A
skills-only variant can select, reorder, or accurately rename confirmed skills;
it must not add unsupported proficiency. Compare all other content with the
master. Experience changes need a user-requested revision.

## PDF gates

For a new master or variant:
1. Verify titles, dates, schools, factual labels, metrics, contact details, and
   skills against the profile and source documents.
2. Compile/export the actual final source. Verify the saved PDF rather than only
   an editor preview. Check the user-selected page count and paper size.
3. Extract text; inspect names, dates, bullet order, missing glyphs, and reading
   order. `verify_pdf.py` helps with extraction and page count; it is not a
   complete layout or factual checker.
4. Render every page and inspect clipping, spacing, alignment, headings, bullet
   labels, and excess whitespace. Do not shrink text or invent filler to force fit.
5. If a reviewer is requested, provide the rendered artifact, posting, facts,
   and changes. Resolve findings before registration.
6. Register the exact PDF and archive its hash. For unchanged copies, hash equality
   permits reuse of the PDF review. The application itself still needs review.

Use a neutral candidate-facing filename. Keep employer, version, and requisition
in the parent directory. New master versions make pending attachments stale;
replace them and recheck parsing. Never overwrite an already-submitted artifact.

For a reviewed skills-only version, use `register-resume --variant --pdf PATH
--reviewed --review-note TEXT`. It archives the variant without changing the
master pointer. The tool checks the master mapping is still current; the reviewer
must verify that non-skills content is unchanged. Record the returned variant hash
in that application's receipt.

## Role descriptions

Transcribe only each employment record's final reviewed bullets into the
profile's `employment[].bullets`. Compare them to the source and rendered PDF.
The registration command produces `role-descriptions.json` beside the frozen PDF.
It does not automatically extract or verify the source wording.

Each point begins with ASCII `- ` on a new line, with real newline characters.
Join visual wraps into one logical bullet. Exclude employer/title/date/location
headings. Keep separate jobs at the same company separate. Do not enter academic
projects as employment. Paste these descriptions exactly into duties fields.

Check each description after entry and after saving, including wording, count,
order, and line breaks. If a review page collapses newlines, inspect the saved
editable value. For a field limit, prepare a supported shorter version and record
the deviation; never silently truncate or describe it as an exact match.

## Form gates

- Confirm account identity, legal/preferred names, contact details, and referral
  evidence. A preserved URL alone does not prove employer-side referral attribution.
- Verify all employment records against the profile, twice: after parsing/manual
  entry and on final review. Use the candidate's actual record count, not a fixed
  number. Correct missing/merged entries, current status, internship labels, dates,
  titles, location, and descriptions.
- Verify all requested education records, degree status, subjects, and dates.
  A current degree is not a completed degree. Do not turn projects into paid work.
- Verify the actual retained attachment and version. A matching filename or a
  successful chooser call alone does not prove upload success or remote hash.
- Answer the exact question from confirmed facts. Prior employment, relationships,
  referrals, criminal history, and professional licenses are distinct questions.
- Keep authorization and sponsorship answers scoped to the stated country, time,
  and restriction. Resolve a contradiction instead of choosing the favorable answer.
- Required motivation answers should connect a concrete employer problem to real
  experience. Avoid generic praise, invented interests, and unrelated visa text.
- Use genuine examples for tests, methods, software, results, and deadlines. If the
  method is unknown, ask; do not fill a plausible statistical method as history.
- Respect self-completion declarations and assessment/interview integrity rules.
  Hand off work that requires the applicant's independent response.
- Confirm salary currency and hourly/annual basis. Do not infer take-home pay or
  compare annualized internship figures without stating the conversion assumptions.
- Honor optional contact/demographic preferences and required document instructions.
  A different transcript is not equivalent to a current-term transcript.

Save the review evidence privately. The reviewer can check captured form details,
but only the main operator changes the live form and verifies corrections.

## Submission and recovery

Follow `final_submit` and platform overrides, plus the connected tool's current
rules. Default setup leaves final submission to the user. Obtain any required
agreement/credential/CAPTCHA handoff at the action point; do not repeatedly ask
about an unchanged action already approved where the tool permits reuse.

After submission, require a success message, correct requisition in candidate
home, or explicit user confirmation. Account creation, a draft save, a timeout,
or a closed tab is not confirmation. Check status before any retry.

Record the outcome and exact PDF hash locally; then update and verify the tracker
before proceeding. If sync fails, record pending sync and continue authorized work.
Do not resend an application to fix a tracker failure.
