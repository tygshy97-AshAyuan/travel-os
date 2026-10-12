# Client validation record

This record separates package installation evidence from model-behavior claims.

## Codex on Windows - 2026-10-12

Environment: Codex desktop on Chinese Windows, using the bundled `skill-installer` and `skill-creator` validation scripts.

| Check | Evidence | Result |
|---|---|---|
| Install from GitHub tag | `install-skill-from-github.py --repo tygshy97-AshAyuan/travel-os --path skill/travel-os --ref v0.4.16` | Passed |
| Installed template bootstrap | Installed `validate_archive.py` returned `READY` for the installed blank workbook | Passed |
| Official Skill format validation | `quick_validate.py` against the installed Skill | Found and fixed a Windows locale incompatibility caused by Unicode arrows in `SKILL.md` |
| Fixed candidate installation | Standard installer fetched the pushed fix branch with its Git sparse-checkout method | Passed |
| Fixed package validation | Official validator returned `Skill is valid!`; installed template returned `READY`; the contract suite also enforces ASCII-compatible `SKILL.md` bytes | Passed |

The final v0.4.16 package was installed globally. Its 12 tracked files matched the tagged source by SHA-256, the blank template returned `READY`, and the official Skill validator returned `Skill is valid!`.

## End-to-end fictional workbook - 2026-10-12

Environment: Codex desktop on Chinese Windows, using the installed v0.4.16 Skill and the repository's fictional `TravelOS-Example.xlsx` as a read-only source.

| Workflow check | Workbook evidence | Result |
|---|---|---|
| Recovery | Loaded `DEMO-001`, active `v0.1.0`, members, constraints and pending `PR-001` before any write | Passed |
| Owner-approved change | Owner `M-001` accepted `PR-001`; successor `v0.1.1` retained stable item IDs and predecessor history | Passed |
| Execution update | Active items became `Done`; the linked booking and original checklist became completed | Passed |
| Weather unavailable | Recorded a bounded recheck task and explicitly preserved the itinerary instead of inventing a forecast | Passed |
| Post-trip memory | Added confirmed long-term preference `P-002` with subject, evidence and effective date | Passed |
| Writeback validation | Repository validator returned `PASS`; formula-error scan found 0 matches; all affected sheets were rendered and visually checked | Passed |

The generated workbook contains only fictional data. It is retained as local test evidence rather than committed to the public repository, avoiding a second binary fixture that would duplicate the canonical example.

## Codex on Windows package regression - v0.4.31

Environment: Codex desktop on Chinese Windows, using the standard `skill-installer` against the public GitHub tag in an isolated local destination.

| Check | Evidence | Result |
|---|---|---|
| Install from current GitHub tag | `install-skill-from-github.py --repo tygshy97-AshAyuan/travel-os --path skill/travel-os --ref v0.4.31` | Passed |
| Published content identity | All 12 installed files exactly matched the Git objects archived from `v0.4.31:skill/travel-os` | Passed |
| Official Skill format validation | `quick_validate.py` against the isolated installed Skill | Passed |
| Installed template bootstrap | Installed validator returned `READY` for the installed blank workbook | Passed |
| Retained end-to-end archive | Installed validator returned `PASS` for the fictional planning, change, execution, weather-fallback and review workbook | Passed |

This repeat confirms that the accumulated schema and validator changes through v0.4.31 remain installable and accept the retained full-lifecycle evidence. It does not claim a new model-behavior run because this release series did not change `SKILL.md` workflow instructions.

## Remaining client evidence

The original run proves one complete supported-client behavior path, and the v0.4.31 regression proves the latest package and workbook contract. Neither proves universal model compliance. Repeat the full model-behavior scenario after changes to `SKILL.md` workflow instructions or spreadsheet write tooling; repeat package and archive validation after schema or validator changes.
