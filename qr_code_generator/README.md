# QR Code Generator for QGIS

[![Release](https://img.shields.io/github/v/release/Heed725/QR-Code-Generator-Qgis-Plugin?label=release)](https://github.com/Heed725/QR-Code-Generator-Qgis-Plugin/releases)
[![Security checks](https://github.com/Heed725/QR-Code-Generator-Qgis-Plugin/actions/workflows/security.yml/badge.svg)](https://github.com/Heed725/QR-Code-Generator-Qgis-Plugin/actions/workflows/security.yml)
[![QGIS](https://img.shields.io/badge/QGIS-3.22--4.x-589632)](https://qgis.org/)
[![Qt](https://img.shields.io/badge/Qt-5%20%7C%206-41CD52)](https://www.qt.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Generate QR codes and common linear barcodes, then copy them, save them as PNG
or insert them directly into QGIS Print Layout as editable Picture items.

## Supported codes

- QR Code
- Code 128 and Code 39
- EAN-13 and EAN-8
- UPC-A
- GS1-128
- ITF

## Features

- Accepts links, text, product numbers and other supported values.
- Selectable foreground and background colours, including transparency.
- Configurable output width, QR error correction and quiet-zone size.
- Live preview and clipboard copy.
- High-resolution PNG export.
- Direct QGIS Print Layout integration.
- Adds **Add QR Code / Barcode** to open layout menus and toolbars.
- Stores layout assets beside the project when possible.
- Self-contained release with QR and barcode encoders bundled.
- Supports QGIS 3.22 through QGIS 4.x and Qt5/Qt6.

## Installation

1. Download [`qr_code_generator-0.0.1.zip`](https://github.com/Heed725/QR-Code-Generator-Qgis-Plugin/releases/download/0.0.1/qr_code_generator-0.0.1.zip).
2. In QGIS, open **Plugins → Manage and Install Plugins**.
3. Select **Install from ZIP** and choose the downloaded file.
4. Approve the installation and enable **QR Code Generator**.

Use the named release asset above, not GitHub's automatically generated
**Source code (zip)** archive. The correct package contains the bundled
encoders under `qr_code_generator/vendor/`.

## Normal QGIS usage

1. Click **Generate QR / Barcode** or use **Plugins → QR Code Generator**.
2. Choose the code type and enter its link, text or numeric value.
3. Choose the colours and output size.
4. For QR codes, select error correction and quiet-zone size.
5. Generate the image, then copy it or save it as PNG.

## Print Layout usage

1. Open or create a QGIS Print Layout.
2. Click **Add QR Code / Barcode** in the layout Items menu or toolbar.
3. Configure and generate the code.
4. Click **Add to Print Layout**.
5. Move, resize, align, duplicate or lock the resulting Picture item normally.

Generated layout images are saved in a `.qr_barcode_assets` folder beside the
QGIS project when possible so that the Picture item remains available later.

## Barcode notes

QR codes accept general text and URLs. EAN and UPC formats require correctly
sized numeric values. The bundled encoder validates barcode content and
calculates checksums where supported.

## Changelog

Version 0.0.1 generates QR Code, Code 128, Code 39, EAN-13, EAN-8, UPC-A, GS1-128 and ITF images with configurable colours, size, QR error correction and quiet zones. Generated codes can be previewed, copied, saved as PNG or inserted directly into QGIS Print Layout as editable Picture items. This release adds QGIS 3.22 through QGIS 4.x and Qt5/Qt6 compatibility, scoped colour, image, painter and layout enums, explicit cleanup logging, complete repository metadata, bundled qrcode and python-barcode dependencies, automated security checks and a verified installable release ZIP.

## Licensing

The plugin is released under the [MIT License](LICENSE). Bundled `qrcode` and
`python-barcode` retain their upstream licenses; see
[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
