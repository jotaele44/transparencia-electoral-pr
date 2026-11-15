# Transparencia Electoral PR

Independent, nonpartisan, evidence-first electoral transparency producer for Puerto Rico. **RC1: development only; no validated election data or production integration.**

## Scope

- Audit official election result versions with stable identifiers, full row conservation, and provenance.
- Preserve CEE source references and only promote independently verified source manifestations.
- Review election-specific findings without duplicating MoneySweep's canonical campaign finance/procurement data.
- Use Centinelas for advance official signals, Spiderweb for spatial bridges, and TheHub as the sole federation product surface.

## Tests

`python3 -m unittest discover -s tests -v`

`federation.json` is fail-closed: discovery and live execution remain disabled pending independent QA and authorization.
