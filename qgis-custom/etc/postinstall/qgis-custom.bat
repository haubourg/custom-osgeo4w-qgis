@REM install QGIS custom launcher 
@echo on
echo "Starting postinstall qgis-custom .bat"

set APPNAME=QGIS CUSTOM (LTR)

@REM Modify QGIS_WIN_APP_NAME and re-do --postinstall.
@REM Avoid the creation of default QGIS Desktop shortcut (https://trac.osgeo.org/osgeo4w/ticket/694)
for %%i in ("%OSGEO4W_STARTMENU%") do set QGIS_WIN_APP_NAME=%%~ni\%APPNAME%
call "%OSGEO4W_ROOT%\bin\qgis-ltr.bat" --postinstall

set O4W_ROOT=%OSGEO4W_ROOT%
set OSGEO4W_ROOT=%OSGEO4W_ROOT:\=\\%

@REM  backup native QGIS bat files and shortcuts

move /Y "%OSGEO4W_ROOT%\bin\qgis-ltr.bat" "%OSGEO4W_ROOT%\bin\qgis-ltr-natif.bat"

@REM git does not sync empty folder, create the backup folder just in case
mkdir "%OSGEO4W_ROOT%\apps\qgis-custom\qgis-ltr-backup\startmenu_links"

move /Y "%AppData%\Microsoft\Windows\Start Menu\Programs\QGIS3.lnk" "%OSGEO4W_ROOT%\apps\qgis-custom\qgis-ltr-backup\startmenu_links"
move /Y "%OSGEO4W_STARTMENU%\*" "%OSGEO4W_ROOT%\apps\qgis-custom\qgis-ltr-backup\startmenu_links"

@REM  delete of backup link (may remain from previous install)
del "%OSGEO4W_ROOT%\apps\qgis-custom\qgis-ltr-backup\%APPNAME%.lnk"

@rem copy launcher and make a shortcut in start menu
move /Y "%OSGEO4W_ROOT%\apps\qgis-custom\qgis-ltr-custom.bat.template" "%OSGEO4W_ROOT%\bin\qgis-ltr-custom.bat"

echo on

if not %OSGEO4W_MENU_LINKS%==0 if not exist "%OSGEO4W_STARTMENU%" mkdir "%OSGEO4W_STARTMENU%"
if not %OSGEO4W_DESKTOP_LINKS%==0 if not exist "%OSGEO4W_DESKTOP%" mkdir "%OSGEO4W_DESKTOP%"

if not %OSGEO4W_MENU_LINKS%==0 xxmklink "%OSGEO4W_STARTMENU%\%APPNAME%.lnk" "%OSGEO4W_ROOT%\bin\qgis-ltr-custom.bat" "" "%DOCUMENTS%" "" 1 "%OSGEO4W_ROOT%\apps\qgis-ltr\icons\qgis.ico"
if not %OSGEO4W_DESKTOP_LINKS%==0 xxmklink "%OSGEO4W_DESKTOP%\%APPNAME%.lnk" "%OSGEO4W_ROOT%\bin\qgis-ltr-custom.bat" "" "%DOCUMENTS%" "" 1 "%OSGEO4W_ROOT%\apps\qgis-ltr\icons\qgis.ico"

@REM file associations

textreplace -std -t "%OSGEO4W_ROOT%\apps\qgis-custom\bin\qgis-custom-ltr.reg"
set OSGEO4W_ROOT=%O4W_ROOT%

@REM Do not register extensions if release is installed
if not exist "%OSGEO4W_ROOT%\apps\qgis-custom\bin\qgis-custom-ltr.reg" "%WINDIR%\regedit" /s "%OSGEO4W_ROOT%\apps\qgis-custom\bin\qgis-custom-ltr.reg"
del /s /q "%OSGEO4W_ROOT%\apps\qgis-ltr\python\*.pyc"

echo "End of qgis-custom postinstall"

@echo off
exit /b 0
