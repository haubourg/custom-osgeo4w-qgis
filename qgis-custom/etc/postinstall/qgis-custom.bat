@REM install QGIS custom launcher 
@echo on
echo "Starting postinstall qgis-custom .bat"

set OSGEO4W_ROOT=%OSGEO4W_ROOT:\=\\%

@REM  backup native QGIS bat files and shortcuts

move /Y "%OSGEO4W_ROOT%\bin\qgis-ltr.bat" "%OSGEO4W_ROOT%\bin\qgis-ltr-natif.bat"

move /Y "%AppData%\Microsoft\Windows\Start Menu\Programs\QGIS3.lnk" "%OSGEO4W_ROOT%\apps\qgis-custom\qgis-ltr-backup\startmenu_links\
move /Y "%OSGEO4W_STARTMENU%\*" "%OSGEO4W_ROOT%\apps\qgis-custom\qgis-ltr-backup\startmenu_links\

@REM  delete of backup link (may remain from previous install)
del "%OSGEO4W_ROOT%\apps\qgis-custom\qgis-ltr-backup\QGIS CUSTOM (LTR).lnk"


@rem copy launcher and make a shortcut in start menu
move /Y "%OSGEO4W_ROOT%\apps\qgis-custom\qgis-ltr-custom.bat.template" "%OSGEO4W_ROOT%\bin\qgis-ltr-custom.bat"

nircmd shortcut "%OSGEO4W_ROOT%\bin\nircmd.exe" "%OSGEO4W_STARTMENU%" "QGIS custom (LTR)" "exec hide ~q%OSGEO4W_ROOT%\bin\qgis-ltr-custom.bat~q" "%OSGEO4W_ROOT%\apps\qgis-ltr\icons\qgis.ico" 

@REM file associations

textreplace -std -t "%OSGEO4W_ROOT%\apps\qgis-custom\bin\qgis-custom-ltr.reg"
nircmd elevate "%WINDIR%\regedit" /s "%OSGEO4W_ROOT%\apps\qgis-custom\bin\qgis-custom-ltr.reg"

echo "End of qgis-custom postinstall"

@echo off
exit /b 0
.lnk