# RC19 — Legal-source and conditional HTTP acquisition audit

## Preserved baselines
RC18 `cceea9dea0dcb75edbac29d6307293234f719f59`; main `b90b4e78f3e6cd66f5e78d508ad590a15e569eb0`. Work remains isolated.

## Ley 39-2026 and article renumbering
The official SUTRA record identifies PS0717 / Ley 39-2026 and links the enacted PDF at `https://sutra.oslpr.org/SutraFilesGen/158328/0039s0717.pdf`. The official document endpoint returned HTTP 403 to browser and direct retrieval. Therefore the official original signed PDF is LOCATED BUT BYTES_NOT_ACQUIRED; no SHA-256 is asserted. LexJuris supplies a secondary reproduction, not the original.

Section 45 of Ley 39 amends former Article 9.35, Solicitud del Voto Ausente, and places the 50-day application requirement in subsection (5). Section 49 renumbers former Articles 9.19–9.39 as 9.20–9.40, so the amended provision is current Article 9.36(5). Section 69 says the law takes effect 30 days after approval. The 2026-04-09 date is a computed date, pending formal legal-date review.

## CEE 45-day public guidance vs current 50-day statute
The CEE JAVAA information page continues to say an absentee application is due 45 days before the election and cites Article 9.35(4). The OGP consolidated Electoral Code, revision 2026-11-04, states 50 days in Article 9.36(5). The CEE webpage is therefore stale in both its stated deadline and article/subsection reference relative to the current consolidated statute.

Do not confuse the 50-day Puerto Rico application deadline with the separate UOCAVA 45-day ballot-transmission rule in 52 USC 20302(a)(8) for qualifying absent uniformed-services and overseas federal voters. The latter is a ballot-transmission obligation when a valid request is received at least 45 days before the federal election; it is not the Puerto Rico application deadline.

This establishes an official public-information discrepancy, not proof of how JAVAA actually processed applications, voter impact, disenfranchisement, or a statutory violation.

## JAVAA instructions
The CEE 2026 regulations index was inspected; it displays no JAVAA-specific 2028 absentee/advance voting regulation. The accessible CEE JAVAA regulation is titled for 2024 primaries and the 2024 general election and approved 2024-08-30. Its provisions cannot automatically be carried forward as the operative 2028 rules after Ley 39 and subsequent changes. No current 2028 JAVAA operational manual was located in this bounded search.

## 2028 calendar and date scope
Official CEE documents were recovered as public locators and visually inspected: CEE-RS-26-010 (8 pages; signed presidential resolution dated 2026-09-08) and CEE-AC-26-149 (3 pages; disagreement certification dated 2026-08-27). These are official records, but the latter is a disagreement record and the former resolves a specific advance-mail dispatch issue; neither is the full comprehensive event calendar.

CEE-RS-26-010 sets advance-mail dispatch to begin as soon as ballots are available, no later than 2028-09-20, and finish no later than 2028-10-03. The 2028-09-23 date in the resolution concerns the UOCAVA transmission deadline for qualifying requests. The modalities and populations differ; do not call them conflicting dates.

CEE-AC-26-149 contains a source-name contradiction: the document page says `ASUNTO: CALENDARIO ELECTORAL 2026`, while the CEE registry and substantive discussion concern the 2028 calendar. Preserve both strings. The 21-page 2026-09-29 calendar copy hosted by the PIP commissioner's site remains a secondary-hosted candidate, not an authenticated CEE original. Full calendar event and amendment denominators remain unknown.

## RC19 HTTP adapter
`src/rc19_http.py` implements opt-in, one-request-at-a-time, GET-only acquisition; HTTPS and exact host allowlisting; redirect blocking; 10 MB default cap; 30-second maximum timeout; PDF signature and content-length validation; ETag and Last-Modified conditional headers; 304 handling; and SHA-256 over returned raw bytes. Bytes are returned in memory only. The adapter has no filesystem persistence, scheduler, alerts, public publishing, or enforcement. ETags and Last-Modified are metadata, not content identity. A 404 or other missing response does not prove deletion.

Network fetch has not been run against CEE or SUTRA sources. The HTTP adapter is validated with mocked response fixtures only. Production network egress and DNS controls would require separate security review.

## Certification
Source original-byte SHA-256 count remains zero. Full calendar, JAVAA 2028 manual, event and amendment denominators remain open. Pinned cross-repo runtime validation, rollback testing and independent legal/security/privacy/evidence QA remain open. RC19 is AUDIT_ONLY; no production release or main merge.


## Exact pinned consumer validation (2026-11-17)
At exact repository commits, RC19 checked Centinelas, MoneySweep, Spiderweb and TheHub manifests and schemas. Synthetic-only tests validated the Centinelas signal schema; TheHub source, entity, relationship, observation and source-monitor schemas; Spiderweb's source-monitor schema; and producer manifest contracts. Spiderweb's source-monitor schema Git blob matches TheHub's pinned schema. Centinelas' exporter declares the source_monitors stream and uses the source_monitor_row helper. The pinned Centinelas exporter itself was not executed.

The actual TheHub `validate_package` function at pinned commit `b7a60e613fecb36448c719651625892b2bded565` accepted a synthetic package containing sources, observations and source_monitors. Negative regressions corrupted a source row, fabricated a last-success time when basis was NOT_RECORDED, and falsified the monitor row count; TheHub rejected each case.

MoneySweep is an explicit integration boundary: its pinned federation manifest sets `ready_for_hub_live_execution=false`, and its export-manifest schema's stream enum does not include `source_monitors`. RC19 tested that the core manifest passes and the source_monitors stream fails. No bypass or activation was attempted. Spiderweb exporter runtime was not run.

CI receipts:
- 422/422 unit and negative tests: run 44047443193.
- Pinned producer schema/manifest compatibility: run 44047443208.
- Actual pinned TheHub package validator: run 44047443143.

These are software and schema-compatibility PASS results. They do not establish production monitoring, real election data integration, legal compliance, or independent certification.

## RC19 final boundaries
No CEE/SUTRA live HTTP poll was performed. The adapter is tested with mocked HTTP responses, including 200, 304, redirects, 404, network failure, ETag/Last-Modified, checksum, content-length and size limits. Original source bytes remain 0 acquired and 0 SHA-256 frozen. No producer repository or main branch was modified. Independent QA and cross-repository rollback testing remain open.
