"""Remove unused vendor files and apply small security-scan compatibility fixes."""

from pathlib import Path
import shutil
import sys


def replace_required(path, old, new):
    """Replace known upstream text and fail if the pinned package changed."""
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError("Expected text was not found in {}".format(path))
    path.write_text(text.replace(old, new), encoding="utf-8")


def main(vendor_dir):
    """Prepare the two pinned libraries for the QGIS release package."""
    vendor = Path(vendor_dir).resolve()
    if not (vendor / "qrcode" / "main.py").is_file():
        raise RuntimeError("The pinned qrcode package was not installed.")
    if not (vendor / "barcode" / "writer.py").is_file():
        raise RuntimeError("The pinned python-barcode package was not installed.")

    unused_directories = (
        vendor / "qrcode" / "tests",
    )
    for directory in unused_directories:
        if directory.exists():
            shutil.rmtree(directory)

    unused_files = (
        vendor / "barcode" / "pybarcode.py",
        vendor / "qrcode" / "compat" / "etree.py",
    )
    for path in unused_files:
        if path.exists():
            path.unlink()

    replace_required(
        vendor / "qrcode" / "main.py",
        "            assert issubclass(image_factory, BaseImage)\n",
        "            if not issubclass(image_factory, BaseImage):\n"
        "                raise TypeError(\"image_factory must inherit BaseImage\")\n",
    )
    replace_required(
        vendor / "barcode" / "writer.py",
        "import xml.dom.minidom\n",
        "import xml.dom.minidom  # nosec B408\n",
    )
    replace_required(
        vendor / "barcode" / "writer.py",
        "    assert imp is not None\n",
        "    if imp is None:\n"
        "        raise RuntimeError(\"The XML DOM implementation is unavailable\")\n",
    )
    replace_required(
        vendor / "barcode" / "writer.py",
        "            assert ImageFont is not None\n",
        "            if ImageFont is None:\n"
        "                raise RuntimeError(\"Pillow image fonts are unavailable\")\n",
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: prepare_vendor.py PATH_TO_VENDOR")
    main(sys.argv[1])
