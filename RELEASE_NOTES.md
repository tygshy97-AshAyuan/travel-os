# Travel OS v0.4.7

Version integrity fix.

Travel OS now treats Version plus Item ID as the Daily Plan identity. An itinerary item can keep the same stable ID when copied from one version to the next, while duplicate items inside the same version are still rejected. Daily Plan rows must also reference a version recorded in Change Log.

The release includes a directly installable `Travel-OS-Skill-v0.4.7.zip`, the full repository archive and checksums for both. The package passes 26 contract tests.
