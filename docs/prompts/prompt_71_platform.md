# Prompt 71 - Platform

## User Prompt

```text
Can you go thru all the documents and usuer manual and make sure everything is correct, up-to-date and not stale, and then re-generate the flat file. Use the standard workflow to commit changes to git.
```

## Work Summary

Reviewed current project documentation and user-facing documentation for stale statements after Platform V1, Evaluation Access V1, production deployment, and Platform V2 roadmap work. Updated stale documentation references and regenerated `project_flat_file.txt` as an on-request review snapshot.

## Files Updated

- `README.md`
- `docs/account_management/implementation/account_management_v1.md`
- `docs/deployment/production_readiness_review.md`
- `docs/prompts/README.md`
- `project_flat_file.txt`

## Implementation Commit

`ff82c3e77e0e9ba05fee48667ebc30f58bb076ae`

## Verification Results

```text
git diff --check: PASS
current-doc stale scan: PASS for targeted stale patterns
flat-file sensitive-pattern scan: PASS; only historical prompt text mentioning private-key search markers was found
```

## Snapshot Notes

`project_flat_file.txt` was regenerated with:

- 401 included files;
- 20 binary files represented by metadata only;
- `project_flat_file.txt` excluded from itself;
- local environment files, local databases, media/runtime uploads, caches, virtual environments, `.git`, and build artifacts excluded;
- no actual secret material detected by the snapshot-generation checks.

The full `project_flat_file.txt` patch is intentionally not duplicated in this prompt archive because doing so would embed a full repository snapshot inside another prompt record. The committed snapshot is the authoritative flat-file artifact.

## Commit Stat

```text
ff82c3e Refresh documentation and flat-file snapshot
 README.md                                          |    38 +-
 .../implementation/account_management_v1.md        |     2 +-
 docs/deployment/production_readiness_review.md     |    14 +-
 docs/prompts/README.md                             |    12 +-
 project_flat_file.txt                              | 60345 +++++++++++--------
 5 files changed, 34232 insertions(+), 26179 deletions(-)
```

## Documentation Diff

```diff
commit ff82c3e77e0e9ba05fee48667ebc30f58bb076ae
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 15 13:12:39 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 15 13:12:39 2026 -0700

    Refresh documentation and flat-file snapshot

diff --git a/README.md b/README.md
index 50a1769..e1598a0 100644
--- a/README.md
+++ b/README.md
@@ -1,13 +1,16 @@
-# Vancouver Minor Baseball – Main Site (https://vancouverminor.com)
+# Vancouver Minor Baseball / VCB Platform
 
-This repository contains the primary public-facing site for Vancouver Minor Baseball. It highlights the club’s philosophy, programs, and achievements, and lives alongside other apps that occupy their own subdomains (for example `dev.vancouverminor.com`).
+This repository contains the public-facing Vancouver Minor Baseball site and the VCB Platform used for baseball operations.
 
 The project now also includes:
 
+- `players`: canonical player identity, imports, matching, provenance, and tags
+- `accounts`: account management, authentication workflows, account operations, and user-player links
+- `analytics`: evaluations, review workflows, command center summaries, player profiles, timelines, comparison, and draft context
 - `drafts`: staff-facing draft operations
-- `pdp`: a reusable Player Development Platform for evaluations, goals, snapshots, roadmaps, report cards, drills, and future AI integrations
+- `pdp`: legacy/transitionary player-development functionality that remains installed until an explicit migration/retirement plan is approved
 
-Detailed PDP documentation is in [docs/pdp.md](/Users/eugenelin/dev/vmba0/docs/pdp.md).
+Platform architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Legacy PDP notes live in [docs/archive/pdp.md](docs/archive/pdp.md).
 
 Platform product strategy lives in [docs/product/](docs/product/), including the [Platform V2 Roadmap](docs/product/PLATFORM_V2_ROADMAP.md).
 
@@ -17,11 +20,11 @@ The stack is intentionally lightweight:
 - **Plain HTML/CSS** (no frontend build tooling) keeps the site easy to maintain.
 - **Static assets** (images, CSS) live under `static/`.
 
-Because the project is simple, most customization happens through data dictionaries and templates rather than a database.
+For the public-facing home site, most content customization happens through data dictionaries and templates. Operational platform apps such as `accounts`, `players`, `analytics`, and `drafts` use Django models, migrations, services, and templates documented under `docs/`.
 
 ---
 
-## Project Layout
+## Public Site Layout
 
 ```
 ├── README.md                     # You are here
@@ -336,22 +339,13 @@ Because the apex domain shares infrastructure with other subdomains:
 3. Run through the site on mobile and desktop whenever you touch CSS.
 4. Document any new deployment steps in this README so future developers stay aligned.
 
-## Prompt Registry
+## Prompt Archive
 
-Reusable project prompts live in `prompts/`.
+Historical and reusable Codex prompts live in [docs/prompts/](docs/prompts/).
 
-- Store each prompt as a Markdown file.
-- Name prompt files with the format `[new app name]_prompt_[id].md`.
-- Use lowercase app names and underscores when the app name has multiple words.
-- Start prompt IDs at `0` and increment by `1` for each new prompt.
-- Use the next unused integer ID when creating a new prompt.
+- Name prompt files with the format `prompt_[ID]_[app_name].md`.
+- Use the next unused zero-padded integer ID.
+- Use `platform` when a prompt spans multiple subsystems.
+- Treat prompt files as historical execution records; current architecture and user guidance live under `docs/`.
 
-Example: `analytics_prompt_0.md`
-
-Current analytics prompt session:
-
-```bash
-codex resume 019f15b0-39b4-75a2-97ff-26808c125814
-```
-
-With this structure and deployment workflow, future developers can confidently maintain the `home.vancouverminor.com` subdomain alongside the organization’s other applications. 
+With this structure and deployment workflow, future developers can maintain the public site and the VCB Platform from the same repository.
diff --git a/docs/account_management/implementation/account_management_v1.md b/docs/account_management/implementation/account_management_v1.md
index 2a5fc3d..672aa3b 100644
--- a/docs/account_management/implementation/account_management_v1.md
+++ b/docs/account_management/implementation/account_management_v1.md
@@ -69,7 +69,7 @@ Do not implement these in Account Management v1:
 - `docs/analytics/architecture/03_analytics.md`
 - `docs/analytics/architecture/04_imports.md`
 - `docs/analytics/implementation/repository_assessment.md`
-- `docs/pdp.md`
+- `docs/archive/pdp.md`
 - `docs/archive/prompts/pdp_prompt.md`
 - `docs/archive/prompts/scholarship.md`
 
diff --git a/docs/deployment/production_readiness_review.md b/docs/deployment/production_readiness_review.md
index 8f1edc7..2f96bf1 100644
--- a/docs/deployment/production_readiness_review.md
+++ b/docs/deployment/production_readiness_review.md
@@ -4,15 +4,17 @@ Date: 2026-07-10
 
 Scope: engineering review only. This document does not deploy code, modify settings, create migrations, or reproduce the production-only `vancouverminor/settings.py`.
 
+Status: historical pre-deployment review. The production upgrade described as a future action in this document was completed on 2026-07-11 and is recorded in [Production Deployment - 2026-07-11](production_deployment_2026_07_11.md). Keep this document as the readiness record that informed that deployment.
+
 ## Executive Summary
 
-The current repository should not replace the production code in a direct `git pull` without preparation.
+At the time of this review, the repository should not replace the production code in a direct `git pull` without preparation.
 
-The production deployment is currently based on commit `551dd0de458ba09628dc85183ef04f9e778fa98f` with local, uncommitted production edits to `vancouverminor/settings.py`. The repository has advanced substantially since that revision. It now includes completed Players V1, Analytics V1, Account Management V1, Platform V1 Account Operations, and Evaluation Access V1.
+At the time of this review, production was based on commit `551dd0de458ba09628dc85183ef04f9e778fa98f` with local, uncommitted production edits to `vancouverminor/settings.py`. The repository had advanced substantially since that revision and included completed Players V1, Analytics V1, Account Management V1, Platform V1 Account Operations, and Evaluation Access V1.
 
-The main blockers are configuration and migration readiness, not a need for a different database engine. Production must preserve domain/static/media settings, rotate and externalize the Django secret key, install the new apps in settings, add the account password-change middleware, update login settings, install current dependencies, run all new migrations, and collect static files before switching traffic to the new code.
+The main blockers were configuration and migration readiness, not a need for a different database engine. Production needed to preserve domain/static/media settings, rotate and externalize the Django secret key, install the new apps in settings, add the account password-change middleware, update login settings, install current dependencies, run all new migrations, and collect static files before switching traffic to the new code.
 
-Go/no-go recommendation: **NO-GO for direct replacement today. GO only after the required production changes and a rehearsed backup/migration/rollback sequence are completed.**
+Historical go/no-go recommendation: **NO-GO for direct replacement at review time. GO only after the required production changes and a rehearsed backup/migration/rollback sequence were completed.**
 
 ## Repository Status
 
@@ -381,9 +383,9 @@ Secret rotation rollback:
 
 ## Final Go/No-Go Recommendation
 
-Recommendation: **NO-GO for direct replacement by pulling current `main` over the production checkout.**
+Historical recommendation: **NO-GO for direct replacement by pulling then-current `main` over the production checkout.**
 
-Recommendation: **GO for a planned deployment only after blockers are resolved.**
+Historical recommendation: **GO for a planned deployment only after blockers were resolved.**
 
 Required conditions for GO:
 
diff --git a/docs/prompts/README.md b/docs/prompts/README.md
index e81171c..85d234d 100644
--- a/docs/prompts/README.md
+++ b/docs/prompts/README.md
@@ -40,11 +40,11 @@ The prompt record should include:
 The normal workflow is:
 
 1. Complete the requested file changes.
-2. Update `project_flat_file.txt`.
-3. Commit the requested work with a concise message based on the work completed.
-4. Generate the commit diff.
-5. Add the diff to the prompt record.
-6. Update `project_flat_file.txt` again.
-7. Commit the prompt record separately.
+2. Commit the requested work with a concise message based on the work completed.
+3. Generate the commit diff.
+4. Add the diff to the prompt record.
+5. Commit the prompt record separately.
 
 Do not include unrelated user changes in either commit.
+
+Do not regenerate or update `project_flat_file.txt` during normal prompt archival. The flat file is an on-request artifact only.
```
