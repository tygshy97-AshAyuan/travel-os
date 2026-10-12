# Travel OS v0.4.16

Windows client-install compatibility update.

Travel OS has now been installed from GitHub with Codex's standard Skill Installer and checked with the official Skill validator on Chinese Windows. The test found that Unicode arrows in `SKILL.md` could make a legacy locale-dependent validator fail before parsing the Skill; those characters are now ASCII and protected by a regression test.

The installed package's bundled archive validator also returned `READY` for its blank template. The release includes a directly installable `Travel-OS-Skill-v0.4.16.zip`, the full repository archive and checksums for both. The package passes 43 contract tests.
