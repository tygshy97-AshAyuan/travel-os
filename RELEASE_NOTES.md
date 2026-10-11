# Travel OS v0.4.5

GitHub Early Access safety and presentation update.

The project page now shows Travel Overview and Daily Plan rendered directly from the fictional example workbook, so visitors can assess the product before downloading it.

The runtime validator now treats uploaded XLSX files as untrusted: it limits ZIP entry count, total uncompressed size and individual XML size, and rejects XML DOCTYPE declarations before parsing. The package passes 23 contract tests. Direct mailbox synchronization and supported-client behavior evaluation remain pending.
