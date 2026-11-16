# META-2028 — Puerto Rico Election Transparency & Accountability Program (candidate charter)

## Mission and scope
Primary: prepare a nonpartisan, independently auditable 2028 electoral-process monitoring system covering official calendar/deadlines, public regulatory and administrative decisions, authoritative electoral-unit geographies, public election-technology acceptance, source-version changes, reporting-unit denominators, custody dispositions and complaints/appeals. Historical 2012/2016/2020/2024 audits are selectively scoped regression/weakness evidence, never automatic allegations.

## Boundaries
- **Detection and evidence preservation only.** No interference with electoral infrastructure, voter targeting, persuasion, automatic complaint filing, sanctioning, public findings, or external system writes.
- Distinguish source-published, discovered, fetched, byte-frozen, identity-bound, reconciled, independently reviewed and certified. Public-document absence is not nonexistence.
- Historical findings classify DOCUMENTED_FAILURE / TRANSPARENCY_GAP / SOURCE_CONTRADICTION / RECONCILIATION_FAILURE / UNRESOLVED. Fraud is **never** inferred from discrepancy, absence, delay or association.
- Never infer identity from names, equal counts, normalized precinct identifiers, district overlap, proximity, or election-cycle continuity. Require primary identity bindings and temporal scope.
- Protect voter secrecy, ePoll Book identities, personal voter records and election system security details. Public output is explicit allowlist and synthetic fixtures until authorization.
- Publicly claimed compliance requires documented legal authority, applicable deadline epoch, signed original, known denominator and independent review. Automated alerts classify provisional discrepancies, not guilt.

## Software release gates
Prohibit main merge, live federation, production writes, automatic outgoing alerts, external complaints, public real-case release or skill promotion until exact version/commit + source hashes, independent QA, provenance, legal scope, privacy testing, consumer integration, isolated rollback and explicit separate authorization all PASS. A green CI badge proves software tests only.
Current RC16 status: AUDIT_ONLY. No production authorization.

## Workstreams
P0 calendar & event monitors; P0 official unit-ID registry; P0 source version/result reconciliation; P0 custody/disposition chain; P0 neutral incident lifecycle; P1 IT/procurement acceptance; P1 public records access and case dispositions; P1 synthetic public preview.

## Evidence invariant
Every in-scope item must record exact source identity, authority, event time, publication time, retrieval time, modality, geographic grain, raw identifiers, original/normalized/canonical distinction, content SHA or null, and all unresolved dependencies. Missing required records remain UNKNOWN, never zero.

## Delivery strategy
Initial pilot: 2028 official milestone monitoring plus 2024 Isabela Unit73, CEE statistical-version and retention/disposition historical negative tests. Preserve RC1–RC15 original evidence, update by append-only new observations, no historical rewrite. No bulk acquisition.

## Proposed acceptance tests
Detect missing published document; reject invalid source authority; detect corrected/reissued documents; preserve equal-timestamp source contradictions; reject cross-epoch unit merge; reject municipal result versus college act; test missing/duplicate records and denominator failure; enforce human role separation and no public real-case output; verify pinned TheHub package **in isolated test only**; independent security/privacy/legal QA outstanding.
