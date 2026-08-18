def classFactory(iface):
    from .plugin import QRCodeGeneratorPlugin
    return QRCodeGeneratorPlugin(iface)
