# QR Code Generator for QGIS

A QGIS plugin for creating QR codes and common linear barcodes, with direct QGIS Print Layout integration.

## Features

- Generate **QR Code**, **Code 128**, **Code 39**, **EAN-13**, **EAN-8**, **UPC-A**, **GS1-128**, and **ITF**.
- Generate from a URL, text, product number, or other supported barcode value.
- Pick **any foreground color** and **any background color**.
- Live preview.
- Export as high-resolution PNG.
- Copy the generated code to the clipboard.
- Add the generated QR/barcode directly to **QGIS Print Layout**.
- Adds **Add QR Code / Barcode…** to the Print Layout **Items** menu and Actions toolbar.
- Inserted layout codes are normal QGIS **Picture** items, so they can be moved, resized, aligned, duplicated, locked, and exported with the map layout.
- Self-contained release ZIP with both encoder dependencies bundled.

## Installation

### Recommended: GitHub Release

1. Open the repository **Releases** page.
2. Download `qr_code_generator-qgis-v1.1.0.zip`.
3. In QGIS, open **Plugins → Manage and Install Plugins…**.
4. Select **Install from ZIP**.
5. Choose the downloaded ZIP and install it.
6. Enable **QR Code Generator**.

## Normal QGIS usage

1. Click the **Generate QR / Barcode** toolbar button, or use **Plugins → QR Code Generator**.
2. Choose the code type.
3. Paste a website link, enter text, or enter the barcode value.
4. Choose foreground and background colors.
5. Set the output width.
6. For QR codes, choose error correction and quiet-zone size.
7. Click **Generate / Refresh**.
8. Use **Save PNG…**, **Copy**, or **Add to Print Layout**.

## Print Layout usage

1. Open **Project → Layout Manager** and open or create a Print Layout.
2. Look in the Print Layout **Items** menu or the Actions toolbar.
3. Click **Add QR Code / Barcode…**.
4. Choose QR Code or one of the supported linear barcode formats.
5. Enter the link/value and choose colors.
6. Click **Generate / Refresh**.
7. Click **Add to Print Layout**.
8. The plugin creates a QGIS Picture item near the top-left of the layout and selects it automatically.
9. Move, resize, align, duplicate, or style the item using normal QGIS layout controls.

The plugin saves generated layout image assets in a `.qr_barcode_assets` folder beside the QGIS project when possible. This keeps the Picture item source available when the project/layout is reopened.

## Barcode notes

- QR Code accepts general text and URLs.
- Code 128 is a good general-purpose one-dimensional barcode for text and numbers.
- EAN/UPC formats require correctly sized numeric values; the encoder validates them and calculates checksums where supported.
- Linear barcodes use vector SVG internally for rendering before being converted to the high-resolution image inserted into the layout.

## Compatibility

- QGIS 3.22+
- Windows, Linux and macOS
- No external Python package installation is required when using the packaged GitHub Release ZIP.

## Development

The source tree intentionally does not vendor third-party dependencies. The release workflow creates a build directory and installs:

- `qrcode==8.2`
- `python-barcode==0.16.1`

into `qr_code_generator/vendor` before creating the distributable ZIP.

The Print Layout integration uses QGIS' `layoutDesignerOpened` / `layoutDesignerWillBeClosed` interfaces and adds the plugin action to every open layout designer.

## Release automation

`.github/workflows/release.yml` validates the Python source, packages the self-contained plugin, and publishes `v1.1.0` with `qr_code_generator-qgis-v1.1.0.zip`.

## License

MIT for this plugin. Bundled third-party packages retain their own licenses; see `THIRD_PARTY_LICENSES.md`.
