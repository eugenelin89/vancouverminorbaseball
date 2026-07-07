**Must-Fix Before Phase 3**

1. Unresolved rows can be permanently locked into a committed batch.  
   In [players/services/import_service.py](/Users/eugenelin/dev/vmba0/players/services/import_service.py:652), rows with errors, unresolved conflicts, or ambiguous matches are skipped, but the batch is always marked `COMMITTED` at [line 687](/Users/eugenelin/dev/vmba0/players/services/import_service.py:687). That prevents staff from returning to resolve the remaining rows. This is the highest-risk issue.

2. Ambiguous matches cannot actually be resolved.  
   The conflict UI offers “Commit if possible” in [analytics/templates/analytics/import_conflicts.html](/Users/eugenelin/dev/vmba0/analytics/templates/analytics/import_conflicts.html:18), but the service always skips ambiguous rows at [players/services/import_service.py](/Users/eugenelin/dev/vmba0/players/services/import_service.py:665). The architecture says ambiguous matches require staff review before merge; right now there is review, but no merge path.

3. Matching only uses the first source identifier.  
   `_match_identity()` takes only `source_identifiers[0]` at [players/services/import_service.py](/Users/eugenelin/dev/vmba0/players/services/import_service.py:435). If a CSV row includes multiple identifiers and the first one misses but another would match, the import may create duplicate players.

**Should-Fix**

1. Raw CSV data is retained broadly and visible in admin-editable JSON fields.  
   `preview_snapshot` stores parsed source rows in [PlayerImportBatch](/Users/eugenelin/dev/vmba0/players/models.py:135), and committed rows preserve `original_row` in [PlayerSourceRow](/Users/eugenelin/dev/vmba0/players/models.py:174). That fits provenance, but admin currently does not make those fields read-only or intentionally scoped in [players/admin.py](/Users/eugenelin/dev/vmba0/players/admin.py:50). Since these are youth player records and source CSVs may contain DOB or contact-adjacent data, admin exposure should be deliberate.

2. The preview page allows direct confirmation even when rows need review.  
   [analytics/templates/analytics/import_preview.html](/Users/eugenelin/dev/vmba0/analytics/templates/analytics/import_preview.html:58) always shows “Confirm Import.” Staff can bypass the conflict page and accidentally skip unresolved rows.

3. First/last name changes are not treated as conflicts.  
   `CONFLICT_FIELDS` excludes `first_name` and `last_name` in [players/services/import_service.py](/Users/eugenelin/dev/vmba0/players/services/import_service.py:65). If an identifier matches but the name differs, the imported name is silently treated as metadata unless existing fields are blank.

4. There is no CSV size or row-count guard.  
   `parse_player_csv()` reads the whole upload into memory at [players/services/import_service.py](/Users/eugenelin/dev/vmba0/players/services/import_service.py:208), then stores parsed rows in JSON. A large accidental upload could be painful.

**Nice-To-Have**

1. Improve DOB parsing transparency. Ambiguous formats like `05/06/2012` are parsed using `%m/%d/%Y` before `%d/%m/%Y` at [players/services/import_service.py](/Users/eugenelin/dev/vmba0/players/services/import_service.py:297). For Canadian data, this should eventually be explicit or warned.

2. Make import summary labels clearer. `updated` increments when a matched player is processed, even if no player fields changed, at [players/services/import_service.py](/Users/eugenelin/dev/vmba0/players/services/import_service.py:671). That may confuse staff.

3. Split tests out of the growing monolithic [players/tests.py](/Users/eugenelin/dev/vmba0/players/tests.py:221) before Phase 3 adds more domains.

**Recommended Fixes**

- Block final commit while unresolved conflicts/errors/ambiguous rows remain, unless staff explicitly skips them.
- Add a real ambiguous-match resolution control: choose an existing candidate, create new, or skip.
- Update `_match_identity()` to try all source identifiers before falling back to name/DOB matching.
- Make sensitive import JSON fields read-only in admin and consider hiding raw payloads from default admin forms.
- Disable or relabel “Confirm Import” on preview when review rows exist.
- Add tests for unresolved conflict retry behavior, ambiguous candidate selection, multiple identifier matching, non-staff access, and privacy/admin read-only behavior.

**Can Phase 3 Safely Begin?**

Not yet. The app boundary is mostly correct and Analytics is thin, but Phase 3 depends on stable canonical player identity. The unresolved-batch and ambiguous-match behavior can leave imports incomplete or duplicate-prone, which would contaminate later observations. I would fix the must-fix items before starting Phase 3.