@REM  puts back QGIS native launchers and file associations 

echo "running .bat preremove qgis-custom "

set O4W_ROOT=%OSGEO4W_ROOT%
set OSGEO4W_ROOT=%OSGEO4W_ROOT:\=\\%

set APPNAME=QGIS custom (LTR)

@REM  deletes .bat et and custom shortcuts
del "%OSGEO4W_ROOT%\bin\qgis-ltr-custom.bat"
del "%OSGEO4W_STARTMENU%\%APPNAME%..lnk"
del "%OSGEO4W_DESKTOP%\%APPNAME%..lnk"

@REM del "%OSGEO4W_ROOT%\bin\qgis-ltr-custom-bin.vars"
@REM del "%OSGEO4W_ROOT%\bin\qgis-ltr-custom-bin.env"

@REM cleans python compiled files (should be adapted to Python3 cache)
del /s /q "%OSGEO4W_ROOT%\apps\qgis-custom\python\*.pyc"

@REM deletes custom shortcut backup (may remain)
del "%OSGEO4W_ROOT%\apps\qgis-custom\qgis-ltr-backup\%APPNAME%.lnk"

@REM delete old reg key association

del "%OSGEO4W_ROOT%\apps\qgis-custom\bin\qgis-custom-ltr.reg"

@REM restore native shortcuts

move /Y "%OSGEO4W_ROOT%\bin\qgis-ltr-natif.bat" "%OSGEO4W_ROOT%\bin\qgis-ltr.bat"

move /Y "%OSGEO4W_ROOT%\apps\qgis-custom\qgis-ltr-backup\startmenu_links\*.lnk" "%OSGEO4W_STARTMENU%\"


@REM  replays file associations for qgs / qgz with QGIS native

set OSGEO4W_ROOT=%OSGEO4W_ROOT:\=\\%
textreplace -std -t "%OSGEO4W_ROOT%\apps\qgis-ltr\bin\qgis.reg"
if not exist "%OSGEO4W_ROOT%\apps\qgis\bin\qgis.reg" "%WINDIR%\regedit" /s "%OSGEO4W_ROOT%\apps\qgis-ltr\bin\qgis.reg"
