# RC22 — Targeted source discovery and isolated rollback evidence

## Baselines
RC21 exact `4ef2e3a03395accc23db8d46205333d68af16169`, main exact `b90b4e78f3e6cd66f5e78d508ad590a15e569eb0`. All RC22 writes occur on isolated branch `rc22-election-rollback-isolation`.

## Primary-source investigation
The official CEE agreements index https://www.ceepur.org/acuerdos-de-comision/ includes:
- CEE-AC-26-110, approval of the eRE and eJAVAA systems **test report**; this does not prove current 2028 JAVAA regulation approval, system readiness or cybersecurity.
- CEE-AC-26-204, disposal of some JAVAA material in 2026; not item-level original custody or 2024 Isabela Unit 73 destruction.
- CEE-AC-26-137, approval of 2028 **primaries and nomination** manual; separate from 2028 operative absentee and advance voting regulation.
- The 2028 calendar decision CEE-RS-26-010 is a bounded advance-mail resolution, not a complete authoritative event inventory.

The SUTRA enacted Ley39 document locator remains official but its PDF/DOC bytes are inaccessible via the available interface. No original signed-law SHA256 was produced. SUTRA indexed effective date (2026-04-08) and previously computed clause date (2026-04-09) both remain unresolved pending signed original and legal interpretation. The 2026-11-04 OGP consolidated Code shows the JAVAA draft-regulation duty in Art. 9.42(4), but that does not establish an approved actual 2028 manual. The official CEE full 2028 calendar and complete amendment inventory remain unrecovered.

## Development and tests
`src/rc22_rollback.py` creates five **disposable synthetic** local Git repositories in a temporary folder, alters one to five fixtures, simulates interruption, then restores exact initial commit trees, manifest payload hashes and clean working trees. Does not clone, alter, reset or deploy real GitHub federation repositories. PASS means software fixture rollback works, not that cross-repository production rollback is certified. Legacy pinned Hub validator remains synthetic and its CI must be checked at final exact commit. Centinelas/MoneySweep/Spiderweb actual runtimes not executed.

## No release
Original source bytes, signed 2028 operative JAVAA, official calendar and amendment denominators, actual producer runtime, independently authenticated offdevice recovery and independent legal/security/privacy/evidence QA are unresolved. Production, merge, autonomous allegations and real voter data prohibited. Status AUDIT_ONLY.
