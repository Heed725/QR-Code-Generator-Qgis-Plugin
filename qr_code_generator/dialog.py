import os
import tempfile
import uuid
from io import BytesIO

from qgis.PyQt.QtCore import QByteArray, Qt
from qgis.PyQt.QtGui import QColor, QImage, QPainter, QPixmap
from qgis.PyQt.QtSvg import QSvgRenderer
from qgis.PyQt.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)
from qgis.core import (
    QgsLayoutItemPicture,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsProject,
    QgsUnitTypes,
)


class ColorButton(QPushButton):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self.clicked.connect(self.pick_color)
        self.setMinimumWidth(130)
        self._refresh()

    def color(self):
        return QColor(self._color)

    def pick_color(self):
        chosen = QColorDialog.getColor(
            self._color,
            self,
            "Choose color",
            QColorDialog.ShowAlphaChannel,
        )
        if chosen.isValid():
            self._color = chosen
            self._refresh()

    def _refresh(self):
        self.setText(
            self._color.name(
                QColor.HexArgb if self._color.alpha() < 255 else QColor.HexRgb
            )
        )
        text_color = "#000000" if self._color.lightness() > 140 else "#ffffff"
        self.setStyleSheet(
            "QPushButton { background: %s; color: %s; padding: 6px 10px; "
            "border: 1px solid #777; border-radius: 4px; }"
            % (self._color.name(QColor.HexArgb), text_color)
        )


class QRCodeGeneratorDialog(QDialog):
    CODE_TYPES = (
        ("QR Code", "qr"),
        ("Code 128", "code128"),
        ("Code 39", "code39"),
        ("EAN-13", "ean13"),
        ("EAN-8", "ean8"),
        ("UPC-A", "upca"),
        ("GS1-128", "gs1_128"),
        ("ITF", "itf"),
    )

    def __init__(self, parent=None, plugin_dir=None, layout_designer=None):
        super().__init__(parent)
        self.plugin_dir = plugin_dir or os.path.dirname(__file__)
        self.layout_designer = layout_designer
        self.current_image = None
        self.current_kind = "qr"
        self.setWindowTitle("QR Code & Barcode Generator")
        self.resize(680, 720)
        self._build_ui()
        self._connect_signals()
        self.set_layout_designer(layout_designer)

    def _build_ui(self):
        root = QVBoxLayout(self)

        intro = QLabel(
            "Create QR codes or common linear barcodes, choose any colors, export "
            "them, or place them directly in a QGIS Print Layout."
        )
        intro.setWordWrap(True)
        root.addWidget(intro)

        form = QFormLayout()

        self.type_combo = QComboBox()
        for label, code in self.CODE_TYPES:
            self.type_combo.addItem(label, code)
        form.addRow("Code type:", self.type_combo)

        self.data_edit = QLineEdit()
        self.data_edit.setPlaceholderText("https://example.com or any text")
        self.data_edit.setText("https://qgis.org")
        form.addRow("Link / value:", self.data_edit)

        self.foreground_button = ColorButton("#000000")
        self.background_button = ColorButton("#ffffff")
        form.addRow("Code color:", self.foreground_button)
        form.addRow("Background:", self.background_button)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(128, 4096)
        self.size_spin.setSingleStep(64)
        self.size_spin.setValue(1024)
        self.size_spin.setSuffix(" px")
        form.addRow("Output width:", self.size_spin)

        self.error_combo = QComboBox()
        self.error_combo.addItem("Low (L) — 7%", "L")
        self.error_combo.addItem("Medium (M) — 15%", "M")
        self.error_combo.addItem("Quartile (Q) — 25%", "Q")
        self.error_combo.addItem("High (H) — 30%", "H")
        self.error_combo.setCurrentIndex(1)
        form.addRow("QR error correction:", self.error_combo)

        self.border_spin = QSpinBox()
        self.border_spin.setRange(0, 20)
        self.border_spin.setValue(4)
        form.addRow("QR quiet-zone modules:", self.border_spin)
        root.addLayout(form)

        self.preview = QLabel("Preview")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(420, 360)
        self.preview.setStyleSheet(
            "QLabel { background: #f5f5f5; border: 1px solid #b7b7b7; }"
        )
        root.addWidget(self.preview, 1)

        buttons = QHBoxLayout()
        self.generate_button = QPushButton("Generate / Refresh")
        self.copy_button = QPushButton("Copy")
        self.save_button = QPushButton("Save PNG…")
        self.layout_button = QPushButton("Add to Print Layout")
        self.close_button = QPushButton("Close")
        buttons.addWidget(self.generate_button)
        buttons.addWidget(self.copy_button)
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.layout_button)
        buttons.addStretch(1)
        buttons.addWidget(self.close_button)
        root.addLayout(buttons)

        self.layout_hint = QLabel("")
        self.layout_hint.setWordWrap(True)
        root.addWidget(self.layout_hint)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        root.addWidget(self.status)

        self.generate_code()

    def _connect_signals(self):
        self.generate_button.clicked.connect(self.generate_code)
        self.copy_button.clicked.connect(self.copy_image)
        self.save_button.clicked.connect(self.save_image)
        self.layout_button.clicked.connect(self.add_to_layout)
        self.close_button.clicked.connect(self.close)
        self.data_edit.returnPressed.connect(self.generate_code)
        self.type_combo.currentIndexChanged.connect(self._type_changed)
        self.foreground_button.clicked.connect(self.generate_code)
        self.background_button.clicked.connect(self.generate_code)

    def set_layout_designer(self, designer):
        self.layout_designer = designer
        has_layout = designer is not None
        if hasattr(self, "layout_button"):
            self.layout_button.setEnabled(has_layout)
            self.layout_hint.setText(
                "Print Layout detected. The generated code can be inserted as an editable Picture item."
                if has_layout
                else "Open a QGIS Print Layout to enable direct placement. The plugin also adds an 'Add QR Code / Barcode…' command to the Layout Items menu and toolbar."
            )

    def _type_changed(self):
        is_qr = self.type_combo.currentData() == "qr"
        self.error_combo.setEnabled(is_qr)
        self.border_spin.setEnabled(is_qr)
        if is_qr:
            self.data_edit.setPlaceholderText("https://example.com or any text")
        else:
            self.data_edit.setPlaceholderText("Enter the value required by the selected barcode")
        self.generate_code()

    def _get_qrcode_module(self):
        try:
            import qrcode
            from qrcode import constants
            return qrcode, constants
        except Exception as exc:
            raise RuntimeError(
                "The QR encoder is missing. Install this plugin from the packaged GitHub Release ZIP."
            ) from exc

    def _get_barcode_modules(self):
        try:
            import barcode
            from barcode.writer import SVGWriter
            return barcode, SVGWriter
        except Exception as exc:
            raise RuntimeError(
                "The linear barcode encoder is missing. Install this plugin from the packaged GitHub Release ZIP."
            ) from exc

    def generate_code(self):
        data = self.data_edit.text().strip()
        if not data:
            self.current_image = None
            self.preview.clear()
            self.preview.setText("Enter a link or value first.")
            self.status.setText("")
            return

        self.current_kind = self.type_combo.currentData()
        try:
            if self.current_kind == "qr":
                self.current_image = self._generate_qr_image(data)
            else:
                self.current_image = self._generate_barcode_image(data, self.current_kind)
            self._show_preview()
            self.status.setText("%s generated successfully." % self.type_combo.currentText())
        except Exception as exc:
            self.current_image = None
            self.preview.clear()
            self.preview.setText("Code generation failed")
            self.status.setText(str(exc))

    def _generate_qr_image(self, data):
        qrcode, constants = self._get_qrcode_module()
        correction = {
            "L": constants.ERROR_CORRECT_L,
            "M": constants.ERROR_CORRECT_M,
            "Q": constants.ERROR_CORRECT_Q,
            "H": constants.ERROR_CORRECT_H,
        }[self.error_combo.currentData()]

        qr = qrcode.QRCode(
            version=None,
            error_correction=correction,
            box_size=1,
            border=self.border_spin.value(),
        )
        qr.add_data(data)
        qr.make(fit=True)
        return self._matrix_to_image(qr.get_matrix(), self.size_spin.value())

    def _generate_barcode_image(self, data, barcode_type):
        barcode, SVGWriter = self._get_barcode_modules()
        writer = SVGWriter()
        code = barcode.get(barcode_type, data, writer=writer)
        output = BytesIO()
        code.write(
            output,
            options={
                "foreground": self.foreground_button.color().name(QColor.HexRgb),
                "background": self.background_button.color().name(QColor.HexRgb),
                "module_width": 0.35,
                "module_height": 15.0,
                "quiet_zone": 4.0,
                "font_size": 10,
                "text_distance": 4.0,
                "write_text": True,
            },
        )
        return self._svg_to_image(output.getvalue(), self.size_spin.value())

    def _svg_to_image(self, svg_bytes, requested_width):
        renderer = QSvgRenderer(QByteArray(svg_bytes))
        if not renderer.isValid():
            raise ValueError("The barcode renderer returned invalid SVG data.")

        source = renderer.defaultSize()
        if source.width() > 0 and source.height() > 0:
            height = max(128, int(requested_width * source.height() / source.width()))
        else:
            height = max(128, requested_width // 3)
        height = min(height, requested_width)

        image = QImage(requested_width, height, QImage.Format_ARGB32)
        image.fill(self.background_button.color())
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        return image

    def _matrix_to_image(self, matrix, requested_size):
        modules = len(matrix)
        if modules <= 0:
            raise ValueError("QR encoder returned an empty matrix.")

        scale = max(1, requested_size // modules)
        actual_size = modules * scale
        image = QImage(actual_size, actual_size, QImage.Format_ARGB32)
        image.fill(self.background_button.color())

        painter = QPainter(image)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.foreground_button.color())
        for row_index, row in enumerate(matrix):
            y = row_index * scale
            for col_index, dark in enumerate(row):
                if dark:
                    painter.drawRect(col_index * scale, y, scale, scale)
        painter.end()
        return image

    def _show_preview(self):
        if self.current_image is None:
            return
        pixmap = QPixmap.fromImage(self.current_image)
        width = max(100, self.preview.width() - 12)
        height = max(100, self.preview.height() - 12)
        self.preview.setPixmap(
            pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.FastTransformation)
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_image is not None:
            self._show_preview()

    def copy_image(self):
        if self.current_image is None:
            self.generate_code()
        if self.current_image is not None:
            QApplication.clipboard().setImage(self.current_image)
            self.status.setText("Code image copied to the clipboard.")

    def save_image(self):
        if self.current_image is None:
            self.generate_code()
        if self.current_image is None:
            return

        default_name = "%s-code.png" % self.current_kind.replace("_", "-")
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Code Image",
            default_name,
            "PNG image (*.png)",
        )
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"

        if self.current_image.save(path, "PNG"):
            self.status.setText("Saved: %s" % path)
        else:
            QMessageBox.critical(self, "QR Code & Barcode Generator", "Could not save the PNG file.")

    def add_to_layout(self):
        if self.layout_designer is None:
            QMessageBox.information(
                self,
                "Print Layout",
                "Open a QGIS Print Layout first, then use the plugin button inside the layout window.",
            )
            return

        self.generate_code()
        if self.current_image is None:
            return

        try:
            asset_path = self._save_layout_asset()
            layout = self.layout_designer.layout()
            picture = QgsLayoutItemPicture(layout)
            picture.setPicturePath(asset_path)
            picture.setResizeMode(QgsLayoutItemPicture.Zoom)

            if self.current_kind == "qr":
                width_mm, height_mm = 35.0, 35.0
            else:
                width_mm, height_mm = 65.0, 28.0

            picture.attemptMove(
                QgsLayoutPoint(10.0, 10.0, QgsUnitTypes.LayoutMillimeters)
            )
            picture.attemptResize(
                QgsLayoutSize(width_mm, height_mm, QgsUnitTypes.LayoutMillimeters)
            )
            layout.addLayoutItem(picture)
            self.layout_designer.selectItems([picture])
            self.layout_designer.showItemOptions(picture)
            self.status.setText(
                "%s added to Print Layout. Move and resize it like any other Picture item."
                % self.type_combo.currentText()
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Print Layout",
                "Could not add the generated code to the layout:\n%s" % exc,
            )

    def _save_layout_asset(self):
        project = QgsProject.instance()
        base_dir = project.homePath()
        if not base_dir and project.fileName():
            base_dir = os.path.dirname(project.fileName())
        if not base_dir:
            base_dir = tempfile.gettempdir()

        asset_dir = os.path.join(base_dir, ".qr_barcode_assets")
        os.makedirs(asset_dir, exist_ok=True)
        filename = "%s_%s.png" % (
            self.current_kind,
            uuid.uuid4().hex[:12],
        )
        path = os.path.join(asset_dir, filename)
        if not self.current_image.save(path, "PNG"):
            raise IOError("Could not write layout asset to %s" % path)
        return path
