# Travel OS v0.4.8

First-run bootstrap fix.

The command-line validator now recognizes the untouched canonical workbook as a structurally valid, uninitialized template and reports `READY`. This lets a first-time user proceed into the New trip workflow instead of being stopped by the recovery rule before any trip data exists.

Populated workbooks still receive full strict validation. The release includes a directly installable `Travel-OS-Skill-v0.4.8.zip`, the full repository archive and checksums for both. The package passes 28 contract tests.
