import os
import sys

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction


class QRCodeGeneratorPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.dialog = None
        self.layout_actions = {}

    def initGui(self):
        icon = QIcon(os.path.join(self.plugin_dir, "icon.svg"))
        self.action = QAction(icon, "Generate QR / Barcode", self.iface.mainWindow())
        self.action.setObjectName("QRCodeGeneratorAction")
        self.action.setToolTip("Generate QR codes and linear barcodes, including Print Layout items")
        self.action.triggered.connect(lambda: self.run())

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&QR Code Generator", self.action)

        # QGIS exposes every Print Layout designer to plugins. Add our action to
        # designers which are already open and to every designer opened later.
        self.iface.layoutDesignerOpened.connect(self._on_layout_designer_opened)
        self.iface.layoutDesignerWillBeClosed.connect(self._on_layout_designer_will_close)
        for designer in self.iface.openLayoutDesigners():
            self._attach_layout_action(designer)

    def unload(self):
        try:
            self.iface.layoutDesignerOpened.disconnect(self._on_layout_designer_opened)
        except (TypeError, RuntimeError):
            pass
        try:
            self.iface.layoutDesignerWillBeClosed.disconnect(self._on_layout_designer_will_close)
        except (TypeError, RuntimeError):
            pass

        for designer, action in list(self.layout_actions.items()):
            self._remove_layout_action(designer, action)
        self.layout_actions.clear()

        if self.action is not None:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu("&QR Code Generator", self.action)
            self.action.deleteLater()
            self.action = None
        if self.dialog is not None:
            self.dialog.close()
            self.dialog = None

    def _on_layout_designer_opened(self, designer):
        self._attach_layout_action(designer)

    def _on_layout_designer_will_close(self, designer):
        action = self.layout_actions.pop(designer, None)
        if action is not None:
            self._remove_layout_action(designer, action)
        if self.dialog is not None and self.dialog.layout_designer is designer:
            self.dialog.set_layout_designer(None)

    def _attach_layout_action(self, designer):
        if designer is None or designer in self.layout_actions:
            return

        icon = QIcon(os.path.join(self.plugin_dir, "icon.svg"))
        action = QAction(icon, "Add QR Code / Barcode…", designer.window())
        action.setObjectName("QRCodeGeneratorLayoutAction")
        action.setToolTip("Generate a QR code or barcode and add it directly to this Print Layout")
        action.triggered.connect(lambda checked=False, d=designer: self.run(d))

        designer.itemsMenu().addAction(action)
        designer.actionsToolbar().addAction(action)
        self.layout_actions[designer] = action

    def _remove_layout_action(self, designer, action):
        try:
            designer.itemsMenu().removeAction(action)
            designer.actionsToolbar().removeAction(action)
        except RuntimeError:
            pass
        action.deleteLater()

    def run(self, layout_designer=None):
        vendor_dir = os.path.join(self.plugin_dir, "vendor")
        if os.path.isdir(vendor_dir) and vendor_dir not in sys.path:
            sys.path.insert(0, vendor_dir)

        from .dialog import QRCodeGeneratorDialog

        # If launched from the normal QGIS toolbar, automatically target an
        # already-open Print Layout when one exists.
        if layout_designer is None:
            designers = self.iface.openLayoutDesigners()
            if designers:
                layout_designer = designers[-1]

        if self.dialog is None:
            self.dialog = QRCodeGeneratorDialog(
                self.iface.mainWindow(), self.plugin_dir, layout_designer
            )
        else:
            self.dialog.set_layout_designer(layout_designer)

        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
