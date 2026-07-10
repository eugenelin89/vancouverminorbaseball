# Prompt 65 - Platform

## User Prompt

```text
Regenerate the current repository flat-file snapshot for external architecture and production-readiness review.

This is a snapshot-generation task only.

Do NOT review the code.

Do NOT modify application code.

Do NOT modify normal documentation.

Do NOT refactor, format, or fix unrelated files.

==================================================
Goal
====

Regenerate:

* `project_flat_file.txt`

The new snapshot will replace the stale copy that still contains the previously removed hardcoded Django secret.

The generated snapshot must be safe to upload for architecture, security, performance, production-readiness, documentation, and code-quality review.

==================================================
Before Generating
=================

Read:

* `AGENTS.md`
* `README.md`
* `.gitignore`
* `.env.example`

Confirm:

* `vancouverminor/settings.py` reads `DJANGO_SECRET_KEY` from the environment;
* no hardcoded Django secret remains in active source;
* local `.env` files are ignored;
* the working tree is clean before regeneration.

Do not print or recover the previously committed secret from Git history or the old flat file.

==================================================
Snapshot Requirements
=====================

Regenerate `project_flat_file.txt` from the current repository state.

Use repository-relative paths.

Use deterministic alphabetical ordering.

At the beginning, include:

* repository root;
* generation date and time;
* file count;
* purpose: architecture, security, performance, documentation, and production-readiness review;
* excluded directories and file categories;
* statement that binary files are described but not embedded;
* statement that sensitive values are excluded or redacted.

==================================================
Include
=======

Include relevant tracked project files such as:

* Python source files;
* Django settings and configuration;
* templates;
* tests;
* migrations;
* project documentation;
* README and AGENTS instructions;
* static text/CSS/JavaScript owned by the project;
* deployment configuration examples;
* scripts;
* safe environment example files;
* prompt archives if required by current repository snapshot policy.

Include enough repository context for a full system audit.

==================================================
Exclude
=======

Exclude:

* `.git/`;
* virtual environments;
* `node_modules/`;
* `__pycache__/`;
* `.pytest_cache/`;
* test caches;
* build output;
* coverage output;
* generated static collection output;
* local database files;
* `.env`;
* `.env.*` except `.env.example`;
* editor metadata;
* OS metadata;
* temporary files;
* scratch files;
* logs;
* secrets;
* private credentials;
* dependency caches;
* the previous contents of `project_flat_file.txt` while generating the replacement.

Do not recursively embed `project_flat_file.txt` inside itself.

==================================================
Sensitive-Data Rules
====================

Before writing each file into the snapshot, inspect it for obvious sensitive values.

Sensitive values include:

* Django secret keys;
* API keys;
* access tokens;
* OAuth client secrets;
* database passwords;
* cloud credentials;
* private keys;
* session secrets;
* webhook secrets;
* real `.env` values.

Safe references to environment variable names are allowed, for example:

```text
DJANGO_SECRET_KEY
```

Safe placeholders are allowed, for example:

```text
replace-with-a-secure-random-value
test-only-not-production
[REDACTED]
```

Do not include the old hardcoded Django secret from:

* Git history;
* the stale flat file;
* commit diffs;
* prompt archives;
* cached files.

If a tracked current file contains a probable real secret:

* stop with `BLOCKED`;
* report only the repository-relative file path and variable/key name;
* do not print the value;
* do not generate or commit a partial snapshot.

==================================================
Prompt Archives and Historical Diffs
====================================

Prompt archives may contain historical commit diffs.

Before including them:

* ensure removed secrets are already redacted;
* exclude or redact any historical secret values;
* do not reproduce values from previous commits;
* preserve safe placeholders such as `[REDACTED-REMOVED-SECRET]`.

If safe inclusion cannot be guaranteed, omit the sensitive diff section and note that historical secret-bearing content was excluded.

==================================================
Binary Files
============

Do not embed binary content.

For binary files, include only:

* repository-relative path;
* detected file type;
* size;
* short description when known.

Do not include base64, hex dumps, or raw binary bytes.

==================================================
File Format
===========

Use clear boundaries for every file, such as:

```text
================================================================================
FILE: path/to/file.py
CONTENT-TYPE: text/plain; charset=utf-8
--------------------------------------------------------------------------------
<contents>
```

For excluded/redacted content, use an explicit marker:

```text
[REDACTED — sensitive value loaded from environment]
```

For binary files:

```text
[BINARY FILE — type: image/png, size: 12345 bytes]
```

==================================================
Post-Generation Verification
============================

After generating the snapshot:

1. Search the new `project_flat_file.txt` for obvious secret patterns, including:

   * `SECRET_KEY =`
   * `api_key`
   * `access_token`
   * `client_secret`
   * `password=`
   * `BEGIN PRIVATE KEY`
   * the old removed secret, without printing it

2. Confirm:

   * environment variable names may appear;
   * safe placeholders may appear;
   * no real secret value appears;
   * the stale embedded secret is gone;
   * `project_flat_file.txt` does not contain itself recursively.

3. Verify only these files changed:

   * `project_flat_file.txt`
   * the required prompt archive, if repository policy requires one

4. Run:

```bash
DJANGO_SECRET_KEY=test-only-not-production python manage.py check
git diff --check
```

A full Django test suite is not required for snapshot-only regeneration unless another file changed accidentally.

==================================================
Commit Workflow
===============

Commit the regenerated snapshot first.

Suggested commit message:

```text
Regenerate secure project flat-file snapshot
```

Create the next prompt archive according to `AGENTS.md`.

The prompt archive must not contain the old secret.

Commit the prompt archive separately.

Push both commits.

==================================================
Final Report
============

Report:

* terminal state: PASS or BLOCKED;
* generated snapshot path;
* generation timestamp;
* included file count;
* excluded directory/file summary;
* sensitive-data scan result;
* whether historical prompt diffs required redaction or omission;
* confirmation that the old embedded Django secret is absent;
* confirmation that no real secret was written;
* files changed;
* `manage.py check` result;
* `git diff --check` result;
* commit hashes;
* push result;
* confirmation that no application code was changed.

Do not perform the architecture review in this task.
```

## Implementation Commit

Commit: `f5218254ddabd189e3548db6244999d1ef50e37b`

Message: `Regenerate secure project flat-file snapshot`

Changed files:

```text
project_flat_file.txt
```

Diff summary:

```text
project_flat_file.txt | 105112 +++++++++++++++++++++++++++--------------------
1 file changed, 60677 insertions(+), 44435 deletions(-)
```

Full diff intentionally omitted from this prompt archive because it would duplicate the full repository snapshot. The committed `project_flat_file.txt` is the authoritative generated artifact. The generated snapshot excluded the stale snapshot content while building, did not include binary contents, and did not include the removed hardcoded Django secret.
