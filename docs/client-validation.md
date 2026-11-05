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

## Codex on Windows package regression - v0.4.40

Environment: Codex desktop on Chinese Windows, using the standard `skill-installer` against the public GitHub tag in an isolated local destination.

| Check | Evidence | Result |
|---|---|---|
| Install from current GitHub tag | `install-skill-from-github.py --repo tygshy97-AshAyuan/travel-os --path skill/travel-os --ref v0.4.40` | Passed |
| Published checksums | The public SHA-256 manifest matched both downloaded ZIP assets | Passed |
| Published source identity | All 37 files in the source ZIP and all 12 files in the Skill ZIP exactly matched their tagged Git blobs | Passed |
| Installed content identity | All 12 installed files exactly matched the public Skill ZIP | Passed |
| Official Skill format validation | `quick_validate.py` against the isolated installed Skill | Passed |
| Installed template bootstrap | Installed validator returned `READY` for the installed blank workbook | Passed |
| Canonical example archive | Installed validator returned `PASS` for `TravelOS-Example.xlsx` | Passed |
| Retained end-to-end archive | Installed validator returned `PASS` for the fictional planning, change, execution, weather-fallback and review workbook | Passed |

This repeat confirms that the published v0.4.40 assets match the tagged source, install without modification, and preserve the current workbook contract. It does not claim a new model-behavior run because the release did not change `SKILL.md` workflow instructions.

## skills CLI isolated installation - 2026-11-05

Environment: Linux, Node.js 24.22.1, Python 3.12.14 and `skills@1.7.6`. The public `main` and `v0.5.0` tag both resolved to `6890076c64045a2c43d8c2be520426eba3a4d671`. Each install used a new project directory, not a global agent directory. `DISABLE_TELEMETRY=1` and `DO_NOT_TRACK=1` were set for all CLI checks, so these tests do not establish public adoption or leaderboard activity.

| Check | Evidence | Result |
|---|---|---|
| Repository discovery | `npx --yes skills@1.7.6 add tygshy97-AshAyuan/travel-os --list` | Found exactly `travel-os` |
| Main installation | `npx --yes skills@1.7.6 add tygshy97-AshAyuan/travel-os --skill travel-os --agent codex --copy --yes` | Installed to the isolated project's `.agents/skills/travel-os` |
| Release installation | Same installation command with source `tygshy97-AshAyuan/travel-os@v0.5.0` | Passed |
| Installed content identity | All 19 tracked Skill files in both isolated installs matched the checked source byte for byte | Passed |
| Installed template bootstrap | Installed `scripts/validate_archive.py` against installed `assets/TravelOS-Template.xlsx` | `READY` |
| Installed HTML export | Installed `scripts/export_trip.py` against the fictional canonical example with `--locale en --region mainland-cn` | Exported a read-only HTML file |
| Repository regression | Python unittest discovery, canonical example validation and `node --test tests/test_trip_view.cjs` | 89 Python tests, example validation and 12 JS tests passed |

The CLI discovers `skill/travel-os/SKILL.md` through its recursive fallback; a directory rename is unnecessary. See the CLI's [discovery rules](https://github.com/vercel-labs/skills/blob/main/docs/creating-skills.md) and [telemetry controls](https://github.com/vercel-labs/skills/blob/main/docs/troubleshooting.md#telemetry). These are package/discovery checks, not a new full model-behavior or mobile-device run.

## Remaining client evidence

The 2026-10-27 source update added portable HTML export and regional routing, subsequently published in [v0.5.0](https://github.com/tygshy97-AshAyuan/travel-os/releases/tag/v0.5.0). Its automated/layout evidence and remaining ChatGPT / Codex / mobile checks are tracked separately in [portable-view-validation.md](portable-view-validation.md). The isolated CLI checks above verify installation without changing an existing user's installed Skill.

The original run proves one complete supported-client behavior path; the later regressions prove the package and workbook checks listed for their specific versions. None proves universal model compliance. Repeat the full model-behavior scenario after changes to `SKILL.md` workflow instructions or spreadsheet write tooling; repeat package and archive validation after schema or validator changes.
