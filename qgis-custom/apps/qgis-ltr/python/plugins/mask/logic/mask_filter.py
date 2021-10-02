#! python3  # noqa: E265

from qgis.core import (
    QgsVectorLayer,
    QgsPalLayerSettings,
    QgsProperty,
    QgsMessageLog,
    QgsVectorLayerSimpleLabeling,
)

SPATIAL_FILTER = "in_mask"


def has_mask_filter(layer):
    if not isinstance(layer, QgsVectorLayer):
        return False

    # check if a layer has already a mask filter enabled
    if layer.labeling() is None:
        return False

    settings = layer.labeling().settings()
    show_expr = settings.dataDefinedProperties().property(QgsPalLayerSettings.Show)
    if show_expr is None:
        return False

    return show_expr.expressionString().startswith(SPATIAL_FILTER)


def remove_mask_filter(layer):
    if not isinstance(layer, QgsVectorLayer):
        return False

    # check if a layer has already a mask filter enabled
    if layer.labeling() is None:
        return False

    settings = layer.labeling().settings()

    try:
        if settings.dataDefinedProperties().hasProperty(
            QgsPalLayerSettings.Show
        ) and settings.dataDefinedProperties().property(
            QgsPalLayerSettings.Show
        ).expressionString().startswith(
            SPATIAL_FILTER
        ):
            # new settings
            settings = QgsPalLayerSettings(layer.labeling().settings())
            settings.dataDefinedProperties().setProperty(QgsPalLayerSettings.Show, True)
            if isinstance(layer.labeling(), QgsVectorLayerSimpleLabeling):
                layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    except Exception as e:
        for m in e.args:
            QgsMessageLog.logMessage(m, "Extensions")


def add_mask_filter(layer):
    if not isinstance(layer, QgsVectorLayer):
        return False

    # check if a layer has already a mask filter enabled
    if layer.labeling() is None:
        return False

    try:
        expr = "%s(%d)" % (SPATIAL_FILTER, layer.crs().postgisSrid())
        prop = QgsProperty()
        prop.setExpressionString(expr)

        # new settings
        settings = QgsPalLayerSettings(layer.labeling().settings())
        settings.dataDefinedProperties().setProperty(QgsPalLayerSettings.Show, prop)
        if isinstance(layer.labeling(), QgsVectorLayerSimpleLabeling):
            layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))

    except Exception as e:
        for m in e.args:
            QgsMessageLog.logMessage(m, "Extensions")
