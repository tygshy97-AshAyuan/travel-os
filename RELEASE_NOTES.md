# Travel OS v0.4.9

Preference and row integrity update.

Travel OS now rejects any filled data row that omits its sheet-specific ID, preventing partially written rows from silently escaping relationship and version checks.

Every preference must include its scope, category, priority, subject, concrete statement, evidence and confidence. Post-trip learning rules now distinguish explicit or repeatedly observed preferences from one-off choices and unsupported profile labels. The release includes a directly installable `Travel-OS-Skill-v0.4.9.zip`, the full repository archive and checksums for both. The package passes 30 contract tests.
