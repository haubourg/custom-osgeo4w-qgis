# script that will run qsettings constraints when QGIS starts
# config file :   qgis_constrained_settings.yml
# cf  https://gitlab.com/Oslandia/qgis/qgis-constrained-settings

import yaml
import codecs
import pathlib
import collections
import configparser
import PyQt5.QtCore
import qgis.core


def main():
    application = qgis.core.QgsApplication.instance()
    applicationSettings = qgis.core.QgsSettings(
        application.organizationName(), application.applicationName()
    )
    globalSettingsPath = pathlib.Path(applicationSettings.globalSettingsPath())
    globalSettingsDirPath = globalSettingsPath.parent
    qgisConstrainedSettingsPath = (
        globalSettingsDirPath / "qgis_constrained_settings.yml"
    )

    if not qgisConstrainedSettingsPath.is_file():
        print("No file named {}".format(qgisConstrainedSettingsPath))
        return

    print("Load constrained settings from {}".format(qgisConstrainedSettingsPath))
    with open(str(qgisConstrainedSettingsPath)) as f:
        constrainedSettings = yaml.safe_load(f)

    userSettings = PyQt5.QtCore.QSettings()
    print("Process {}".format(userSettings.fileName()))

    propertiesToRemove = constrainedSettings.get("propertiesToRemove", {})
    for group, properties in propertiesToRemove.items():
        userSettings.beginGroup(group)
        if isinstance(properties, str):
            if properties == "*":
                userSettings.remove("")
        else:
            for prop in properties:
                userSettings.remove(prop)
        userSettings.endGroup()

    globalSettings = configparser.ConfigParser()
    with open(str(globalSettingsPath)) as f:
        globalSettings.read_file(f)

    propertiesToMerge = constrainedSettings.get("propertiesToMerge", {})
    for group, properties in propertiesToMerge.items():
        if not globalSettings.has_section(group):
            continue
        userSettings.beginGroup(group)
        for prop in properties:
            if not globalSettings.has_option(group, prop):
                continue
            userPropertyValues = userSettings.value(prop)
            if not userPropertyValues:
                continue
            if not isinstance(userPropertyValues, list):
                userPropertyValues = [userPropertyValues]
            globalPropertyValues = globalSettings.get(group, prop)
            globalPropertyValues = globalPropertyValues.split(",")
            # codecs.decode(v, "unicode_espace") is used to convert the raw string into a normal
            # string. This is required to avoid changing \\ sequences into \\\\ sequences
            globalPropertyValues = list(
                map(
                    lambda v: codecs.decode(v.strip('" '), "unicode_escape"),
                    globalPropertyValues,
                )
            )
            userPropertyValues = globalPropertyValues + userPropertyValues
            # remove duplicates
            userPropertyValues = list(
                collections.OrderedDict.fromkeys(userPropertyValues)
            )
            userSettings.setValue(prop, userPropertyValues)
        userSettings.endGroup()

    propertyValuesToRemove = constrainedSettings.get("propertyValuesToRemove", {})
    for group, properties in propertyValuesToRemove.items():
        userSettings.beginGroup(group)
        for prop in properties:
            userPropertyValues = userSettings.value(prop)
            if not userPropertyValues:
                continue
            valuesToRemove = list(map(lambda v: v.rstrip("/\\ "), properties[prop]))
            userPropertyValues = [
                v for v in userPropertyValues if v.rstrip("/\\ ") not in valuesToRemove
            ]
            userSettings.setValue(prop, userPropertyValues)
        userSettings.endGroup()


if __name__ == "__main__":
    main()
