# QR Code Generator for QGIS

A lightweight QGIS plugin for creating QR codes directly inside QGIS.

## Features

- Generate QR codes from a URL or any text.
- Pick **any foreground color** using the native QGIS/Qt color picker.
- Pick **any background color**.
- Live QR preview.
- Export as a high-resolution PNG.
- Copy the generated QR code to the clipboard.
- Self-contained release ZIP: the GitHub Actions packaging workflow vendors the QR encoder dependency into the plugin package.

## Installation

### Recommended: GitHub Release

1. Open the repository **Releases** page.
2. Download `qr_code_generator-qgis-v1.0.0.zip`.
3. In QGIS, open **Plugins → Manage and Install Plugins…**.
4. Select **Install from ZIP**.
5. Choose the downloaded ZIP and install it.
6. Enable **QR Code Generator**.

### Usage

1. Click the **QR Code Generator** toolbar button, or use **Plugins → QR Code Generator → Generate QR Code**.
2. Paste a website link or type any text.
3. Choose the QR foreground and background colors.
4. Set the output size and error-correction level.
5. Click **Generate / Refresh**.
6. Use **Save PNG…** or **Copy**.

## Compatibility

- QGIS 3.x
- Windows, Linux and macOS
- No external Python package installation is required when using the packaged GitHub Release ZIP.

## Development

The source tree intentionally does not vendor third-party dependencies. The release workflow copies the plugin source into a build directory and installs the BSD-licensed `qrcode` Python package into `qr_code_generator/vendor` before creating the distributable ZIP.

## Release automation

`.github/workflows/release.yml` builds the plugin ZIP and publishes a GitHub Release when the workflow runs from `main`. The first release is `v1.0.0`.

## License

MIT for this plugin. The packaged `qrcode` dependency retains its own BSD license in the release bundle.
