# Privacy and publishing

## Separation by default

Keep the kit and candidate workspaces separate. The initializer refuses a folder
inside this kit or any other detected Git checkout, creates a private marker, and
adds a defensive ignore-all file. This is not encryption or access control.
Private artifacts stay on the user's machine unless an authorized application,
tracker sync, or other explicitly requested action shares them.

Never copy a populated workspace into a public repository and then try to remove
its details. Build a new export from an explicit allowlist. Do not copy old Git
history, branches, logs, screenshots, resume sources, PDFs, exports, or environment
files. Hidden files, filenames, image metadata, URLs, and commit messages can leak
data even when document text looks sanitized.

No universal professional, demographic, legal-history, or work-authorization
answers are shipped. Defaults are process preferences, not personal facts.

## Publication checks

`public-files.json` is the explicit list of distributable files. The scanner:
- Rejects unlisted files in the public working tree, index, and inspected history.
- Rejects symlinks and unexpected binary files.
- Flags common credential, personal email, home-directory, phone, and tracker-ID patterns.
- Can scan for additional private strings with `--deny-file PATH` (one per line).
  Keep that file outside this repo. Matches are reported by category, not value.

It cannot prove that arbitrary prose contains no personal data. Manually inspect
every exported file, metadata, commit message, and diff before publication.
Do not weaken checks to make a private file publishable.

Optional local hooks in `.githooks/` run the index/history checks before commits
and pushes. Enable them with `git config core.hooksPath .githooks`. Hooks can be
bypassed and are not an access-control boundary; keep private workspaces separate.

Recommended release sequence:

1. Generate a clean distribution in a new folder without Git history.
2. Review each file and the allowlist. Use synthetic examples only.
3. Run `python tests/e2e.py` and `python tools/privacy_scan.py`.
4. Optionally run `python tools/privacy_scan.py --deny-file PATH` with local
   candidate-specific identifiers. Keep the deny file and audit output private.
5. Create a clean backup/export from the allowlist only.
6. Initialize a fresh repository. Stage explicit paths from the allowlist.
7. Run `python tools/privacy_scan.py --mode index`, then inspect the staged diff.
8. Commit and run `python tools/privacy_scan.py --mode history`.
9. Push only after all checks pass and publication is authorized.

The `.gitignore` is defense in depth, not proof that `git add -f` is safe. Never
use candidate data in test fixtures or a demonstration video. Do not include it
in issues, screenshots, public model prompts, or release notes.

## Local records

The toolkit has no telemetry, no cloud upload, and no account-creation code.
The agent's browser and connectors have their own data handling. Review those
services before use. Store only what the workflow needs. Keep credentials in a
password manager and use normal browser sign-in; never put them in the profile.

Use OS permissions and encrypted storage for private workspaces. Back them up
only to a location the user has approved. Removing a local workspace does not
withdraw applications or delete copies already sent to employers or trackers.
