# Some scripts to provide layout pre-print checks - See https://north-road.com/2019/01/14/on-custom-layout-checks-in-qgis-3-6-and-how-they-can-do-your-work-for-you/


from qgis.core import check


@check.register(type=QgsAbstractValidityCheck.TypeLayoutCheck)
def layout_map_crs_choice_check(context, feedback):
    layout = context.layout
    for i in layout.items():
        if isinstance(i, QgsLayoutItemMap):
            for l in i.layersToRender():
                # check if layer source is blacklisted
                if "mt1.google.com" in l.source():
                    res = QgsValidityCheckResult()
                    res.type = QgsValidityCheckResult.Critical
                    res.title = "Blacklisted layer source"
                    res.detailedDescription = 'This layout includes a Google Map layer ("{}"), which is in violation with their Terms of Service'.format(
                        l.name()
                    )
                    return [res]

