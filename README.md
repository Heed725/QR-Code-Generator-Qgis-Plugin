# QR Code Generator for QGIS

[![Release](https://img.shields.io/github/v/release/Heed725/QR-Code-Generator-Qgis-Plugin?label=release)](https://github.com/Heed725/QR-Code-Generator-Qgis-Plugin/releases)
[![Security checks](https://github.com/Heed725/QR-Code-Generator-Qgis-Plugin/actions/workflows/security.yml/badge.svg)](https://github.com/Heed725/QR-Code-Generator-Qgis-Plugin/actions/workflows/security.yml)
[![QGIS](https://img.shields.io/badge/QGIS-3.22--4.x-589632)](https://qgis.org/)
[![Qt](https://img.shields.io/badge/Qt-5%20%7C%206-41CD52)](https://www.qt.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Create QR codes and common linear barcodes, save or copy them, and insert them
directly into QGIS Print Layout as editable Picture items.

## Download

Download [`qr_code_generator-0.0.1.zip`](https://github.com/Heed725/QR-Code-Generator-Qgis-Plugin/releases/download/0.0.1/qr_code_generator-0.0.1.zip),
then install it through **Plugins → Manage and Install Plugins → Install from
ZIP**. Use this named asset because the automatic source archive does not
contain the bundled QR and barcode encoders.

See the [complete plugin guide](qr_code_generator/README.md) for supported code
types, usage, Print Layout instructions and licensing.

## Changelog

Version 0.0.1 generates QR Code, Code 128, Code 39, EAN-13, EAN-8, UPC-A, GS1-128 and ITF images with configurable colours, size, QR error correction and quiet zones. Generated codes can be previewed, copied, saved as PNG or inserted directly into QGIS Print Layout as editable Picture items. This release adds QGIS 3.22 through QGIS 4.x and Qt5/Qt6 compatibility, scoped colour, image, painter and layout enums, explicit cleanup logging, complete repository metadata, bundled qrcode and python-barcode dependencies, automated security checks and a verified installable release ZIP.
