# North Care Memory-Care Discovery Example

Session pattern captured from a client discovery task where Michael provided a Google Drive folder containing a Google Doc transcript and `.m4a` recording for Mac Jones / North Care.

## Useful acquisition workaround

When Drive MCP returned `invalid_grant`, the shared Drive folder was still accessible in-browser. The browser snapshot exposed Drive `data-id` values for the files, enabling direct downloads:

- Google Doc transcript: `https://docs.google.com/document/d/<DOC_ID>/export?format=txt`
- Audio file: `https://drive.google.com/uc?export=download&id=<FILE_ID>`

Capture this as a workaround pattern, not as a claim that Drive MCP is broken.

## Repo split used

- `north-care-source-vault` — private source vault for original audio, original transcript, transcript chunks, and metadata.
- `north-care-reports` — private derived reports only.

The reports repo intentionally did not include a `source/` directory.

## Report series used

1. `01-executive-nuggets.md`
2. `02-pain-point-inventory.md`
3. `03-recruiting-retention-funnel.md`
4. `04-candidate-fit-card-spec.md`
5. `05-facility-priority-map.md`
6. `06-ai-implementation-model.md`
7. `07-data-security-boundary.md`
8. `08-next-actions.md`

## Extraction model

The high-value insight was not merely “North Care needs hiring automation.” It was:

> North Care needs to identify identity-aligned memory-care caregivers, route them by evidence-backed fit/risk/missing info, and onboard them into enough belonging/culture that they survive the first 90 days and become long-term care people.

Useful nugget categories:

- Current assessment cost/speed constraints.
- Wrong-hire cost and turnover economics.
- Stale/recycled candidate sourcing.
- Honest difficulty-based recruiting message.
- Low-friction two-step intake.
- Manager overload/churn loop.
- Onboarding as cultural adhesive / “Ohana.”
- Facility-specific differences.
- AI adoption trust, ROI visibility, and cost-amnesia risk.
- Data-access intimacy and security boundary.

## Verification pattern

For report/source repos with no canonical suite, create a `/tmp/hermes-verify-*` script that checks:

- Expected repos exist.
- Expected README/report/source files exist.
- Source vault contains raw audio/transcript.
- Reports repo does not contain raw source directory.
- Expected report count matches.
- Git status is clean.
- GitHub origin is configured.
- Repo privacy can be verified when using `gh repo view`.

Always summarize as **ad-hoc verification**, not suite green.