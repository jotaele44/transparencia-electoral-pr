# 2028 electoral-readiness objective (RC3)

Objective: independently reconstruct the publicly documented 2024 election processes before permitting 2028 event monitoring to issue authoritative public conclusions.

## Release gates

1. Register legal calendar decisions with distinct signed, publication, effective, and event dates; do not infer unspecified dates.
2. Preserve original source manifestations before attesting hashes: URL metadata and JSON registry hashes are **not** source-payload hashes.
3. Preserve source row identity and all unmatched units; record 1:1 / 1:N / N:1 / N:N / unresolved explicitly.
4. Compare official original, amended, and certified result manifestations without treating a missing row as zero.
5. Keep disputed dates unresolved; a publication or arithmetic discrepancy is not proof of electoral misconduct.
6. Simulate normal, duplicate, late, withdrawn, reissued, and contradictory event streams offline; record first-seen vs legal-event timestamps.
7. Test only isolated read-only exports against TheHub; no new live registration, no security-sensitive system probing.
8. Independent evidence, consumer, security and release QA required before production.

## 2028 calendar evidence

CEE-AC-26-149 (2026-08-27): disagreement about September 27 vs September 20 ballot mailing start.
CEE-RS-26-010 (signed 2026-09-08): ballot mailing start no later than September 20, end no later than October 3, 2028.
CEE RFP-Escrutinio-2028: explicitly says June 6 primary but also first Sunday June; computed first Sunday is June 4. **Contradiction retained, not corrected silently.** General election November 7, 2028.
CEE-AC-26-157 (2026-09-03): 2024 statistical report approved with amendments; source report counts unverified.

No 2024 result-row denominator or original/corrected tally pair has been acquired. No attempt to retrieve voter-specific data.
