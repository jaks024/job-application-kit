# Receipts and tracking

The local SQLite database is the durable record. `add-job` refreshes posting
details but never resets the application state. `record` appends events with
timestamps and evidence. Private screenshots/review files can support a receipt;
do not publish them or include unrelated account information.

## Close out each application

1. Save a JSON event in the private application directory. Include a new UUID,
   exact job key, state, offset-aware timestamp, evidence type, evidence summary,
   submitted resume hash (or null with an explanation), and review-file reference.
2. Run `jobkit.py record --file applications/<job>/event.json`.
3. If Notion is configured and authorized, update its matching row and verify the
   write. Record a separate sync receipt in the same private directory.
4. If a write is uncertain, fetch the destination before retrying. Pending sync
   is a tracker problem, not a reason to repeat an employer submission.

Valid states: New, Prepared, Awaiting user, Blocked, Submission uncertain,
Applied, Interview, Offer, Rejected, Withdrawn, Skipped, Handed off.

Only `portal_confirmation` or explicit `user_confirmation` can establish Applied.
A request to assume completion uses `user_directed_assumption` with Handed off or
Submission uncertain; it is excluded from confirmed totals. An immediate rejection
gets two events: Applied with submission evidence, then Rejected with the reason.
Later search/preparation events do not regress an existing post-submission state.

Reuse the same event ID only when retrying the exact same write. A conflicting
payload with that ID is rejected. Corrections use a new event and explanation;
never edit old evidence in place. The tool does not automatically correct a
wrong original submission date; reconcile such historical errors deliberately.

## Counts

`status --date YYYY-MM-DD` counts distinct job identities by their first confirmed
submission date in the configured candidate timezone, across every batch. It
splits portal- and user-confirmed results. It does not count retries, drafts,
accounts, handoffs, or assumptions. Separate multiple requisitions at one employer.
Subsequent reapplications to the same requisition are not counted as new roles.

## Optional Notion mapping

Use a connected Notion tool; do not store a token in this kit. Ask the user for
the destination and whether to update existing records. Fetch the actual schema
before writing. Suggested properties are Job key, Company, Role, Posting URL,
Status, Priority, Location, Pay, Sponsorship, Posted date, First seen, Applied date,
Review gate, and Evidence. Map to existing names rather than assuming this schema.

Read the complete active and archived roster before creating rows. Incomplete
roster reads block new-row creation, but a known exact row can receive a verified
outcome. Deduplicate using employer/provider job ID or canonical URL, not titles.
Do not recreate an archived application as a new lead.

Preserve human notes and later outcomes. If the tracker only has a small status
vocabulary, retain the detailed local state in Review gate or the page body.
Record rejection separately instead of leaving it as an active Applied role.
Do not archive/delete rows or migrate schemas as part of routine sync.

Use one writer. Read back changed fields or confirm completion of an asynchronous
write. Keep destination IDs and write receipts private. On the next requested
run, reconcile pending sync before presenting new jobs. Local-only mode is fully
supported; no tracker connection should block preparation or accurate receipts.
