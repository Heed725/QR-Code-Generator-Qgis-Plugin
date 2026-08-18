# Changelog

## 1.1.0 — 2026-08-18

- Added direct QGIS Print Layout integration.
- Added **Add QR Code / Barcode…** to each open Print Layout Items menu and Actions toolbar.
- Generated codes can be inserted as normal QGIS Picture items and moved/resized in the layout.
- Added Code 128, Code 39, EAN-13, EAN-8, UPC-A, GS1-128 and ITF linear barcode formats.
- Added persistent project-side `.qr_barcode_assets` storage for layout images.
- Added automatic detection of already-open and newly-opened layout designers.
- Updated the self-contained release package to include `python-barcode` alongside `qrcode`.

## 1.0.0 — 2026-08-18

- Initial QGIS plugin release.
- Generate QR codes from URLs or arbitrary text.
- Select any foreground and background color.
- Configure error-correction level and quiet-zone size.
- High-resolution PNG export.
- Copy generated QR code to clipboard.
- Self-contained GitHub Release package with vendored QR encoder.
