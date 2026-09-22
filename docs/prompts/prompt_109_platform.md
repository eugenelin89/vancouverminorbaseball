# Prompt 109 - Platform

## User Prompt

```text
can you log the audit in a doc in the repo
```

## Implementation Commit

`e1632f0 Document production runtime audit`

## Commit Diff

```diff
diff --git a/docs/deployment/README.md b/docs/deployment/README.md
index adfeca3..9f153b5 100644
--- a/docs/deployment/README.md
+++ b/docs/deployment/README.md
@@ -47,0 +48 @@ Historical deployment records:
+- [Production Runtime Audit - 2026-09-22](production_runtime_audit_2026_09_22.md)
diff --git a/docs/deployment/production_runtime_audit_2026_09_22.md b/docs/deployment/production_runtime_audit_2026_09_22.md
new file mode 100644
index 0000000..0d1317f
--- /dev/null
+++ b/docs/deployment/production_runtime_audit_2026_09_22.md
@@ -0,0 +1,85 @@
+# Production Runtime Audit - 2026-09-22
+
+This is a read-only observation of the production Droplet through its web
+console. It records how the site was running at the time of inspection; it is
+not a deployment approval, a full security assessment, or a record of changes
+made to the server. No secret values were read or copied into this document.
+
+## Request Path
+
+```text
+Browser -> Nginx (HTTPS) -> Gunicorn Unix socket -> Django WSGI application
+                       \-> /static/ and /media/ served directly by Nginx
+```
+
+- Nginx was active and configured for `vancouverminor.com` and
+  `www.vancouverminor.com`. Its HTTP listener redirects to HTTPS; the TLS
+  configuration is managed by Certbot.
+- Nginx proxies application requests to
+  `/var/www/vancouverminorbaseball/vancouverminor.sock`.
+- `/static/` is aliased to `/var/www/vancouverminorbaseball/staticfiles/`.
+  `/media/` is aliased to `/var/www/vancouverminorbaseball/media/`.
+- `vancouverminor.service` was active and enabled. Its systemd unit runs
+  Gunicorn from the project virtual environment with three sync workers,
+  binding to the Unix socket and loading `vancouverminor.wsgi:application`.
+  The service runs as `django-user`, with group `www-data`, from
+  `/var/www/vancouverminorbaseball`.
+- The service loads `/etc/vancouverminorbaseball.env` through systemd. The
+  file was owned by `root:root` with mode `600`. The configured variable
+  names included Django secret, debug, host, static-root and media-root
+  settings, plus the coach import default-password setting. Values were not
+  inspected, except that `DJANGO_DEBUG=false` was verified.
+- The deployed virtual environment reported Django `4.2.30`. The application
+  uses the project SQLite database at
+  `/var/www/vancouverminorbaseball/db.sqlite3`.
+
+## Code And Health State
+
+- The production checkout was on `main` at
+  `c17f2dad2c655f81da0ba242caca4c269c8a843b` (2026-07-27). The
+  service had started after that commit was made, making it likely that the
+  running workers loaded that checkout. A code-to-process checksum was not
+  performed.
+- The production checkout showed no tracked-file modifications. It did have
+  untracked runtime or backup material, including database backups, media,
+  and the virtual environment. Those files must be preserved during future
+  deployment work. The production checkout's `origin/main` tracking state
+  was not refreshed during this audit.
+- At audit time, the local repository's `main` was at `3a351e1`, four commits
+  beyond the production commit. The assessment-workbook import additions
+  and hardening in those commits were therefore not in the production
+  checkout. This comparison is to the local repository, not a claim about
+  the current remote branch.
+- `systemctl is-active` reported both Nginx and `vancouverminor.service`
+  active. A request from the server to `https://vancouverminor.com/`
+  returned HTTP 200.
+
+## Findings To Review
+
+1. **SQLite file permissions:** `db.sqlite3` was owned by `django-user` with
+   mode `644`. Both `/var/www` and the project directory were mode `755`, so
+   other local server users with filesystem access may be able to read the
+   database. This does not by itself expose the database over HTTP. Review
+   least-privilege permissions, the needs of backup jobs, and SQLite sidecar
+   files before making a controlled change.
+2. **Gunicorn socket permissions:** The socket was owned by
+   `django-user:www-data` with mode `777`. Review whether access can be
+   limited to the application and Nginx users without disrupting service.
+3. **Direct media serving:** Nginx serves the media tree directly, outside
+   Django authorization checks. Confirm that uploaded files in this tree
+   are intended to be accessible by URL; keep private documents behind an
+   access-controlled delivery mechanism. This audit did not test individual
+   media URLs or inspect their contents.
+4. **Release gap:** The running deployment predates four local commits. Use
+   the [Deployment Runbook](RUNBOOK.md) and review the intended release,
+   backups, environment, migrations, and rollout before updating production.
+
+## Audit Limits
+
+Only read-only console commands and one public HTTP request were used. No
+code was pulled, migrations run, service restarted, permissions changed, or
+configuration edited. This audit did not validate authenticated workflows,
+Nginx configuration syntax, TLS expiry, database integrity, backup
+restorability, migration state, or the accessibility of individual media
+files. The findings above should be rechecked immediately before any
+production change.
```
