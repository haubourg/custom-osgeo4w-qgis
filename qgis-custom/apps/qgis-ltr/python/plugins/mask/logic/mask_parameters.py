"""
Class to store mask parameters

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import QgsGeometry, QgsProject, QgsFeature, QgsMessageLog
import pickle
import base64


class MaskParameters:
    def __init__(self):
        # selection | mask
        self.do_buffer = False
        self.buffer_units = 1
        self.buffer_segments = 5
        self.do_simplify = True
        self.simplify_tolerance = 1.0
        self.do_save_as = False
        self.file_path = None
        self.file_format = None
        self.style = None
        # polygon mask method : 0: exact, 1: centroid, 2: pointOnSurface
        self.polygon_mask_method = 2
        # line mask method = 0: intersects, 1: contains
        self.line_mask_method = 0
        # layers (list of id) where labeling has to be limited
        self.limited_layers_obsolete = []
        self.orig_geometry = []
        self.geometry = None
        self.do_atlas_interaction = True

    def serialize(self, with_style=True):
        if with_style:
            style = self.style
        else:
            style = None

        t = pickle.dumps(
            [
                self.do_buffer,
                self.buffer_units,
                self.buffer_segments,
                self.do_simplify,
                self.simplify_tolerance,
                self.do_save_as,
                self.file_path,
                self.file_format,
                self.limited_layers_obsolete,
                style,
                self.polygon_mask_method,
                self.line_mask_method,
                [g.asWkb() for g in self.orig_geometry]
                if self.orig_geometry is not None
                else None,
                self.geometry.asWkb() if self.geometry is not None else None,
                self.do_atlas_interaction,
            ],
            protocol=0,
            fix_imports=True,
        )
        return t

    def unserialize(self, st):
        style = None
        orig_geom = None
        geom = None

        try:
            t = pickle.loads(st)
        except:
            try:
                t = pickle.loads(st, encoding="utf-8")
            except Exception as e:
                for m in e.args:
                    QgsMessageLog.logMessage(str(m), "Extensions")

                raise Exception("Mask - Error when loading mask")

        (
            self.do_buffer,
            self.buffer_units,
            self.buffer_segments,
            self.do_simplify,
            self.simplify_tolerance,
            self.do_save_as,
            self.file_path,
            self.file_format,
            self.limited_layers_obsolete,
            style,
            self.polygon_mask_method,
            self.line_mask_method,
        ) = t[0:12]

        if len(t) >= 13:
            orig_geom = t[12]

        if len(t) >= 14:
            geom = t[13]

        if len(t) >= 15:
            self.do_atlas_interaction = t[14]

        self.style = None
        self.geometry = None
        if style is not None:
            self.style = style
        if geom is not None:
            self.geometry = QgsGeometry()
            self.geometry.fromWkb(geom)
        if orig_geom is not None:
            gl = []
            for g in orig_geom:
                geo = QgsGeometry()
                geo.fromWkb(g)
                gl.append(geo)
            self.orig_geometry = gl

    def have_same_layer_options(self, other):
        """Returns true if the other parameters have the same layer options
        (file path, file format) than self
        """
        if not self.do_save_as:
            return not other.do_save_as
        else:
            if not other.do_save_as:
                return False
            else:
                return (
                    self.file_path == other.file_path
                    and self.file_format == other.file_format
                )

    def save_to_project(self):
        serialized = base64.b64encode(self.serialize())
        try:
            QgsProject.instance().writeEntry("Mask", "parameters", serialized)
        except:
            # strange behaviour, pickle change his format ?
            QgsProject.instance().writeEntry(
                "Mask", "parameters", str(serialized)[2:-1]
            )

        return True

    def load_from_project(self):
        st, ok = QgsProject.instance().readEntry("Mask", "parameters")
        if st == "":
            return False

        self.unserialize(base64.b64decode(st))
        return True

    # try to load parameters from a mask layer
    # for compatibility with older versions where parameters were saved in
    # attributes of the mask layer
    def load_from_layer(self, layer):
        # return False on failure
        pr = layer.dataProvider()
        fields = pr.fields()
        if fields.size() < 1:
            return False
        field = None
        for i, f in enumerate(fields):
            if f.name() == "params":
                field = i
        if field is None:
            return False

        it = pr.getFeatures()
        fet = QgsFeature()
        it.nextFeature(fet)
        st = fet.attribute(field)

        self.unserialize(base64.b64decode(st))

        if self.geometry is None:
            self.geometry = QgsGeometry(fet.geometry())
            self.orig_geometry = [QgsGeometry(fet.geometry())]

        return True
