# RC15 — Custody and judicial evidence adjudication

## Pinned baselines
RC14: `7506d46a6d78e7a68450c28677bee6384f2d5786`; main: `b90b4e78f3e6cd66f5e78d508ad590a15e569eb0`. Isolated branch `dev/rc15-custody-legal-provenance`.

## New binding leads and limits
Official CEE commission index lists `CEE-AC-25-006 — Acuerdo depuración de maletines de material electoral 2024 (sobre mesa)`, and `CEE-AC-25-047 — Disposición de material electoral relacionado con acuerdo CEE-AC-25-006`. The listing does not independently establish the first proposal's approval, the scope of any physical material retained, or actual destruction. The associated CEE-AC-25-046 lists status of the depuration project and OSIPE/RGE updates. All original signed record payloads, annexes, inventories and destruction/retention receipts remain missing.

Official index: https://www.ceepur.org/acuerdos-de-comision/

The index status `SOBRE MESA` cannot be promoted to `APPROVED`. A district-level disposition reference cannot establish a specific Isabela 032/Unit73/College identity, physical custody transfer, execution, or a litigation hold.

## Judicial sources
The Tribunal de Apelaciones publicly hosts original `KLAN202500306`, decided 2025-05-22, concerning `SJ2025CV01115`. The PDF was accessed through the official web reader, and page 1 and page 4 screenshots were inspected. The court affirmed the TPI's 2025-03-21 dismissal and fee award; the record discusses appellant claims about ePoll Book signatures and ballot adjudication but does not perform a ballot reconciliation or prove fraud.

Official judgment: https://dts.poderjudicial.pr/ta/2025/KLAN202500306-22052025.PDF

The opinion includes a temporal contradiction: it prints a CEE motion date `24 de febrero de 2024` while describing proceedings filed February 2025. Retain raw text, adjudicate only from original CEE motion in appendix 2 pp. 60–75, and do not silently substitute 2025.

The opinion supplies bounded appendix references for priority exact-document recovery; see `evidence/rc15_court_record_index.json`. Neither the original trial docket nor its attached files were recovered. A targeted attempt to download the appellate PDF raw bytes failed; its SHA256 remains null.

## Electoral-source gaps
CEE-SIP-2025-006 is marked completed 2025-03-28 in CEE's own 2025-03 transparency report, but the original delivered attachment has not been recovered. The report approved with amendments 2026-09-03 is linked from CEE, but its >32 MB web-reader failure remains. No statistical report payload hashes, exact report-table schemas, numerical college denominator, or official OSIPE precinct-unit-college-method export have been acquired.

The source-reported Isabela 032 planning count of 22 units does not disclose all special-modality colleges. Unit 73 is a distinct home-voting modality. No identity binding is licensed from names, leading-zero normalization, nearby precincts, district overlap or source absence.

## Safe next acquisition sequence
1. Obtain CEE-AC-25-006, 25-046 and 25-047 signed originals and all annexes or dispositive inventories, then establish whether any material was actually released/destroyed and its exact precinct/unit/college keys.
2. Obtain OSIPE authoritative precinct-unit-college-scrutiny-method export for 2024, with source epoch and all special modality rosters.
3. Obtain TPI SJ2025CV01115 original judgment and referenced appendices, particularly CEE's motion pp.60–75 and reconsideration disposition pp.192–193.
4. Request redacted Isabela 032/Unit73 actas, results and aggregate ePoll Book totals. Never publish voter identities.
5. Only then attempt complete reporting-unit denominator closure, original/final row-binding and ballot arithmetic.

## Certification
Source manifest `evidence/rc15_primary_discovery.json`, court appendix ledger `evidence/rc15_court_record_index.json`. Original record hashes: 0. Primary Isabela actas: 0. Verified destruction receipts: 0. Actual vote comparisons: 0. Legal, evidence and security independent QA OPEN. No production or main branch authorization; AUDIT_ONLY.
