import os

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QImage, QPainter, QPixmap
from qgis.PyQt.QtWidgets import (
    QApplication,
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
    QWidget,
    QColorDialog,
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
        chosen = QColorDialog.getColor(self._color, self, "Choose color", QColorDialog.ShowAlphaChannel)
        if chosen.isValid():
            self._color = chosen
            self._refresh()

    def _refresh(self):
        self.setText(self._color.name(QColor.HexArgb if self._color.alpha() < 255 else QColor.HexRgb))
        text_color = "#000000" if self._color.lightness() > 140 else "#ffffff"
        self.setStyleSheet(
            "QPushButton { background: %s; color: %s; padding: 6px 10px; border: 1px solid #777; border-radius: 4px; }"
            % (self._color.name(QColor.HexArgb), text_color)
        )


class QRCodeGeneratorDialog(QDialog):
    def __init__(self, parent=None, plugin_dir=None):
        super().__init__(parent)
        self.plugin_dir = plugin_dir or os.path.dirname(__file__)
        self.current_image = None
        self.setWindowTitle("QR Code Generator")
        self.resize(620, 650)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        root = QVBoxLayout(self)

        intro = QLabel(
            "Create a QR code from a web link or any text. Choose any foreground and background colors, then save or copy the result."
        )
        intro.setWordWrap(True)
        root.addWidget(intro)

        form = QFormLayout()
        self.data_edit = QLineEdit()
        self.data_edit.setPlaceholderText("https://example.com or any text")
        self.data_edit.setText("https://qgis.org")
        form.addRow("Link / text:", self.data_edit)

        self.foreground_button = ColorButton("#000000")
        self.background_button = ColorButton("#ffffff")
        form.addRow("QR color:", self.foreground_button)
        form.addRow("Background:", self.background_button)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(128, 4096)
        self.size_spin.setSingleStep(64)
        self.size_spin.setValue(1024)
        self.size_spin.setSuffix(" px")
        form.addRow("Output size:", self.size_spin)

        self.error_combo = QComboBox()
        self.error_combo.addItem("Low (L) — 7%", "L")
        self.error_combo.addItem("Medium (M) — 15%", "M")
        self.error_combo.addItem("Quartile (Q) — 25%", "Q")
        self.error_combo.addItem("High (H) — 30%", "H")
        self.error_combo.setCurrentIndex(1)
        form.addRow("Error correction:", self.error_combo)

        self.border_spin = QSpinBox()
        self.border_spin.setRange(0, 20)
        self.border_spin.setValue(4)
        form.addRow("Quiet-zone modules:", self.border_spin)
        root.addLayout(form)

        self.preview = QLabel("Preview")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(360, 360)
        self.preview.setStyleSheet("QLabel { background: #f5f5f5; border: 1px solid #b7b7b7; }")
        root.addWidget(self.preview, 1)

        buttons = QHBoxLayout()
        self.generate_button = QPushButton("Generate / Refresh")
        self.copy_button = QPushButton("Copy")
        self.save_button = QPushButton("Save PNG…")
        self.close_button = QPushButton("Close")
        buttons.addWidget(self.generate_button)
        buttons.addWidget(self.copy_button)
        buttons.addWidget(self.save_button)
        buttons.addStretch(1)
        buttons.addWidget(self.close_button)
        root.addLayout(buttons)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        root.addWidget(self.status)

        self.generate_qr()

    def _connect_signals(self):
        self.generate_button.clicked.connect(self.generate_qr)
        self.copy_button.clicked.connect(self.copy_image)
        self.save_button.clicked.connect(self.save_image)
        self.close_button.clicked.connect(self.close)
        self.data_edit.returnPressed.connect(self.generate_qr)
        self.foreground_button.clicked.connect(lambda: self._refresh_after_color())
        self.background_button.clicked.connect(lambda: self._refresh_after_color())

    def _refresh_after_color(self):
        # QColorDialog is modal, so this runs after the color is chosen or cancelled.
        self.generate_qr()

    def _get_qrcode_module(self):
        try:
            import qrcode
            from qrcode import constants
            return qrcode, constants
        except Exception as exc:
            raise RuntimeError(
                "The QR encoder is missing. Install this plugin from the packaged GitHub Release ZIP, which includes the dependency."
            ) from exc

    def generate_qr(self):
        data = self.data_edit.text().strip()
        if not data:
            self.current_image = None
            self.preview.setText("Enter a link or text first.")
            self.status.setText("")
            return

        try:
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
            matrix = qr.get_matrix()
            self.current_image = self._matrix_to_image(matrix, self.size_spin.value())
            self._show_preview()
            self.status.setText("QR code generated successfully.")
        except Exception as exc:
            self.current_image = None
            self.preview.setText("QR generation failed")
            self.status.setText(str(exc))

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
        self.preview.setPixmap(
            pixmap.scaled(
                self.preview.size() - self.preview.contentsMargins().topLeft() - self.preview.contentsMargins().bottomRight(),
                Qt.KeepAspectRatio,
                Qt.FastTransformation,
            )
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_image is not None:
            self._show_preview()

    def copy_image(self):
        if self.current_image is None:
            self.generate_qr()
        if self.current_image is not None:
            QApplication.clipboard().setImage(self.current_image)
            self.status.setText("QR code copied to the clipboard.")

    def save_image(self):
        if self.current_image is None:
            self.generate_qr()
        if self.current_image is None:
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save QR Code", "qr-code.png", "PNG image (*.png)")
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        if self.current_image.save(path, "PNG"):
            self.status.setText("Saved: %s" % path)
        else:
            QMessageBox.critical(self, "QR Code Generator", "Could not save the PNG file.")
