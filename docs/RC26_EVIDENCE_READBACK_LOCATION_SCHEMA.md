# RC26 — Independently rehashed RC24 originals and administrative-location contract candidate

## Frozen baselines
RC25 `6dfb162aa5ba7553d655e1953f4230b28bfcddce`, unchanged main `b90b4e78f3e6cd66f5f78d508ad590a15e569eb0`. All code and metadata changes are confined to `dev/rc26-source-readback-schema`.

## Original-source preservation: verified scope
GitHub Actions artifact 14475213513 from run 44408980803 remains unexpired; reported expiry 2027-02-16T22:10:33Z. Its archive was downloaded intact to the temporary ChatGPT working container and independently rehashed on 2026-11-18T23:30:23Z. Exact ZIP SHA256 `553be37c5b5931b1c0e6ff92c652d102c5527772aadf4a4dac32e429fccf95cf`; 23,556,527 bytes. All **14 acquired raw file payloads** were independently SHA256-verified against their embedded source acquisition manifest, as were byte lengths. Manifest denominator: requested=15, acquired=14, failed=1 (OGP Civil Code PDF), blocked=0; no hidden extra payloads. Existing RC24 manifest contains each original's source URL, UTC acquisition and raw hash. The separate PDF and DOC Ley39 manifestations are preserved, never conflated.

This is a **LOCAL_CONTAINER_INDEPENDENT_READBACK**, not off-device restore or durable independent preservation. No approved external storage target was specified; no cloud storage or production writes were made. The GitHub Actions artifact is time-limited, and the user's conversation-file ZIP download does not prove long-term retention. A fresh authorized target must be specified and independently read back before declaring off-device recovery PASS.

`scripts/verify_rc26_archived_sources.py` is a strict offline read-only verifier. It compares the archive SHA256, validates duplicate/path-traversal/symlink/size and record conservation, then independently hashes every original member, forbidding invented missing-source hashes. Tests include forged digests and duplicate/missing records. Original evidence bytes are not added to Git history.

## Centinelas ↔ TheHub location conflict
The exact Centinelas source at `3b80bb5e...` puts municipality name in `observation.location.municipality` when a source identifies an administrative municipality without coordinates. The pinned Hub `b7a60e...` schema currently treats `location` as requiring WGS84 `lat` and `lon`, although its own `hub.correlate._municipality()` reads `location.municipality`. The schema rejects the actual producer stream; it is not a data-integrity fraud finding.

RC26 provides a **proposed, in-memory contract only**: permit a complete WGS84 numeric point OR a municipality-only nongeometric location object, never an unbounded half-point and never synthesized centroids. Preserve the original municipality, its string, and the Hub correlation semantics. The candidate must pass tests with real pinned producer and consumer source code before any governance decision; production and upstream schema are unchanged. A future proposal must explicitly address municipality alias/epoch identity and proximity cannot establish canonical geometry.

## Other source/electoral blockers
RC24 recovered enacted Ley39 PDF+DOC originals and CEE selected minutes. The SUTRA April 8 vs original enacted clause's April 9 computation remains under independent legal review. CEE RFP's raw June 6, 2028 date conflicts with first-Sunday June 4, 2028; RC25 preserves this as noncertified, pending complete binding calendar. Neither a full authoritative 2028 calendar/denominator, current signed 2028 JAVAA regulation, OSIPE original test report and schedule, actual build/deployment receipts nor independent cybersecurity assessment has been recovered.

RC25 full exporter CLI fixtures demonstrate Spiderweb PASS and Centinelas municipality-only location FAIL; MoneySweep source monitor remains unsupported. RC26 candidate schema is disposable, not a production fix or actual full Federation operational acceptance. No new real exporter, producer, or main repository writes.
Status: SOFTWARE TESTS PENDING EXACT HEAD; EVIDENCE PARTIAL; INDEPENDENT QA OPEN; PRODUCTION BLOCKED.
