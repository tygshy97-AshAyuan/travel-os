# Travel OS v0.4.12

Checklist dependency integrity fix.

Travel OS now rejects Checklist dependency cycles. A task cannot wait on itself, and a group of tasks cannot form a loop in which none can begin.

This prevents critical actions such as visa checks, payment and booking confirmation from passing validation while remaining permanently blocked. The release includes a directly installable `Travel-OS-Skill-v0.4.12.zip`, the full repository archive and checksums for both. The package passes 33 contract tests.
