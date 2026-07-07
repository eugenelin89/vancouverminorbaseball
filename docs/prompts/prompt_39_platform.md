# Prompt 39: Platform

## User Prompt

```text
Can you add a rule such that whenever I submit a prompt, if it modifies a file or created a new file or deleted a file , you would paste the prompt in docs/prompts using the format prompt_[prompt_id]_[app_name], commit the changes in git using the resulting output of running the prompt as commit message, and do a diff of the commit from the previous commit, paste the diff into the prompt file you just created. And then commit that file too.
```

## App / Subsystem

platform

## Work Commit

`f83bc1d`

## Work Commit Diff

```diff
diff --git a/AGENTS.md b/AGENTS.md
index 766979a..c048105 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -21,6 +21,28 @@ These instructions apply to the entire repository.
   - binary files represented only by metadata and a short description.
 - Do not embed binary file contents in the snapshot.
 - Exclude `.git`, `.venv`, `__pycache__`, `node_modules`, `dist`, `build`, and the snapshot file itself.
+- Exclude unrelated untracked scratch files unless the user explicitly asks to include them or they were intentionally created as part of the current task.
+
+## Prompt Archive And Commit Policy
+
+When a user prompt causes any file to be created, modified, moved, or deleted:
+
+- Create a prompt record in `docs/prompts/`.
+- Use this filename format:
+
+  ```text
+  prompt_[ID]_[app_name].md
+  ```
+
+- Use the next unused integer ID, zero-padded to two digits.
+- Choose the app/subsystem name that the prompt primarily affects. Use `platform` for cross-subsystem or repository-wide prompts.
+- Paste the user's prompt into the prompt record.
+- Commit the implementation/documentation changes first, using a concise commit message based on the resulting work summary.
+- Generate the diff for that commit against its previous commit.
+- Paste that diff into the prompt record.
+- Commit the prompt record and regenerated `project_flat_file.txt` separately.
+- Do not include unrelated user changes in either commit.
+- If a task cannot be committed safely because the worktree contains unrelated staged changes or an instruction explicitly forbids committing, explain the blocker.

 ## Architecture Boundaries

diff --git a/docs/prompts/README.md b/docs/prompts/README.md
index b193ddd..e81171c 100644
--- a/docs/prompts/README.md
+++ b/docs/prompts/README.md
@@ -25,3 +25,26 @@ These prompts are useful historical context, but they are not the canonical arch
 - [Account Management V1 Summary](../account_management/V1_SUMMARY.md)

 When creating new prompts, use the app/subsystem name that the prompt primarily affects. If a prompt spans multiple subsystems, use `platform`.
+
+## Prompt Records For File-Changing Tasks
+
+When a user prompt creates, modifies, moves, or deletes files, create a prompt record in this folder.
+
+The prompt record should include:
+
+- the user's prompt;
+- the app/subsystem name used for the filename;
+- the commit hash for the resulting work commit;
+- the diff of that work commit against the previous commit.
+
+The normal workflow is:
+
+1. Complete the requested file changes.
+2. Update `project_flat_file.txt`.
+3. Commit the requested work with a concise message based on the work completed.
+4. Generate the commit diff.
+5. Add the diff to the prompt record.
+6. Update `project_flat_file.txt` again.
+7. Commit the prompt record separately.
+
+Do not include unrelated user changes in either commit.
diff --git a/docs/prompts/prompt_39_platform.md b/docs/prompts/prompt_39_platform.md
new file mode 100644
index 0000000..d663883
--- /dev/null
+++ b/docs/prompts/prompt_39_platform.md
@@ -0,0 +1,19 @@
+# Prompt 39: Platform
+
+## User Prompt
+
+```text
+Can you add a rule such that whenever I submit a prompt, if it modifies a file or created a new file or deleted a file , you would paste the prompt in docs/prompts using the format prompt_[prompt_id]_[app_name], commit the changes in git using the resulting output of running the prompt as commit message, and do a diff of the commit from the previous commit, paste the diff into the prompt file you just created. And then commit that file too.
+```
+
+## App / Subsystem
+
+platform
+
+## Work Commit
+
+Pending.
+
+## Work Commit Diff
+
+Pending.
diff --git a/project_flat_file.txt b/project_flat_file.txt
index ebd50d3..6c1c119 100644
--- a/project_flat_file.txt
+++ b/project_flat_file.txt
@@ -1,7 +1,8 @@
 # Project Flat File Snapshot
 # Root: /Users/eugenelin/dev/vmba0
-# File count: 336
+# File count: 335
 # Excluded directories: .git, .venv, __pycache__, node_modules, dist, build
+# Excluded unrelated untracked scratch files.
 # Text files are included as UTF-8/decoded text. Binary files are described, not embedded.

 ====================================================================================================
@@ -44,6 +45,28 @@ These instructions apply to the entire repository.
   - binary files represented only by metadata and a short description.
 - Do not embed binary file contents in the snapshot.
 - Exclude `.git`, `.venv`, `__pycache__`, `node_modules`, `dist`, `build`, and the snapshot file itself.
+- Exclude unrelated untracked scratch files unless the user explicitly asks to include them or they were intentionally created as part of the current task.
+
+## Prompt Archive And Commit Policy
+
+When a user prompt causes any file to be created, modified, moved, or deleted:
+
+- Create a prompt record in `docs/prompts/`.
+- Use this filename format:
+
+  ```text
+  prompt_[ID]_[app_name].md
+  ```
+
+- Use the next unused integer ID, zero-padded to two digits.
+- Choose the app/subsystem name that the prompt primarily affects. Use `platform` for cross-subsystem or repository-wide prompts.
+- Paste the user's prompt into the prompt record.
+- Commit the implementation/documentation changes first, using a concise commit message based on the resulting work summary.
+- Generate the diff for that commit against its previous commit.
+- Paste that diff into the prompt record.
+- Commit the prompt record and regenerated `project_flat_file.txt` separately.
+- Do not include unrelated user changes in either commit.
+- If a task cannot be committed safely because the worktree contains unrelated staged changes or an instruction explicitly forbids committing, explain the blocker.

 ## Architecture Boundaries

@@ -9182,14 +9205,6 @@ class StaffObservationReviewDetailView(AnalyticsStaffRequiredMixin, CoachAssessm
             messages.success(request, "Assessment reopened for editing.")
         return redirect("analytics:observation-review-detail", observation_id=self.observation.pk)

-====================================================================================================
-FILE: /Users/eugenelin/dev/vmba0/db.sqlite3
-====================================================================================================
-CONTENT-TYPE: application/octet-stream
-BINARY-SIZE-BYTES: 1429504
-----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/docs/ARCHITECTURE.md
 ====================================================================================================
@@ -23569,6 +23584,29 @@ These prompts are useful historical context, but they are not the canonical arch

 When creating new prompts, use the app/subsystem name that the prompt primarily affects. If a prompt spans multiple subsystems, use `platform`.

+## Prompt Records For File-Changing Tasks
+
+When a user prompt creates, modifies, moves, or deletes files, create a prompt record in this folder.
+
+The prompt record should include:
+
+- the user's prompt;
+- the app/subsystem name used for the filename;
+- the commit hash for the resulting work commit;
+- the diff of that work commit against the previous commit.
+
+The normal workflow is:
+
+1. Complete the requested file changes.
+2. Update `project_flat_file.txt`.
+3. Commit the requested work with a concise message based on the work completed.
+4. Generate the commit diff.
+5. Add the diff to the prompt record.
+6. Update `project_flat_file.txt` again.
+7. Commit the prompt record separately.
+
+Do not include unrelated user changes in either commit.
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/docs/prompts/prompt_00_analytics.md
 ====================================================================================================
@@ -30664,6 +30702,31 @@ Produce only the engineering planning document.

 The resulting plan should become the roadmap for completing the remaining Platform V1 account-management functionality.

+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/docs/prompts/prompt_39_platform.md
+====================================================================================================
+CONTENT-TYPE: text/plain; charset=utf-8
+----------------------------------------------------------------------------------------------------
+# Prompt 39: Platform
+
+## User Prompt
+
+```text
+Can you add a rule such that whenever I submit a prompt, if it modifies a file or created a new file or deleted a file , you would paste the prompt in docs/prompts using the format prompt_[prompt_id]_[app_name], commit the changes in git using the resulting output of running the prompt as commit message, and do a diff of the commit from the previous commit, paste the diff into the prompt file you just created. And then commit that file too.
+```
+
+## App / Subsystem
+
+platform
+
+## Work Commit
+
+Pending.
+
+## Work Commit Diff
+
+Pending.
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/drafts/README.md
 ====================================================================================================
@@ -52098,17 +52161,3 @@ os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vancouverminor.settings')

 application = get_wsgi_application()

-====================================================================================================
-FILE: /Users/eugenelin/dev/vmba0/vmba0.code-workspace
-====================================================================================================
-CONTENT-TYPE: text/plain; charset=utf-8
-----------------------------------------------------------------------------------------------------
-{
-	"folders": [
-		{
-			"path": "."
-		}
-	],
-	"settings": {}
-}
-

```
