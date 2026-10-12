# Client validation record

This record separates package installation evidence from model-behavior claims.

## Codex on Windows - 2026-10-12

Environment: Codex desktop on Chinese Windows, using the bundled `skill-installer` and `skill-creator` validation scripts.

| Check | Evidence | Result |
|---|---|---|
| Install from GitHub tag | `install-skill-from-github.py --repo tygshy97-AshAyuan/travel-os --path skill/travel-os --ref v0.4.15` | Passed |
| Installed template bootstrap | Installed `validate_archive.py` returned `READY` for the installed blank workbook | Passed |
| Official Skill format validation | `quick_validate.py` against the installed Skill | Found and fixed a Windows locale incompatibility caused by Unicode arrows in `SKILL.md` |
| Fixed candidate installation | Standard installer fetched the pushed fix branch with its Git sparse-checkout method | Passed |
| Fixed package validation | Official validator returned `Skill is valid!`; installed template returned `READY`; the contract suite also enforces ASCII-compatible `SKILL.md` bytes | Passed |

The installer test used a temporary workspace destination and did not modify the user's global Skill directory.

## Remaining client evidence

Installation and static validation do not prove that a model follows every workflow. A fresh supported-client session still needs to run the same fictional archive through recovery, proposal, version change, execution update, weather re-plan and post-trip review. Record the client/version, prompt, input fixture, output and workbook diff without private travel data.
