def classFactory(iface):
    """Return the plugin instance expected by QGIS."""
    from .plugin import QRCodeGeneratorPlugin

    return QRCodeGeneratorPlugin(iface)
