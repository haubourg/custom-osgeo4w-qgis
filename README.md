This project shows how to create a QGIS customized installation for your organization, using the power of [OSGEO4W](https://trac.osgeo.org/osgeo4w/).

QGIS is highly customizable, and most of the tricks are very well documented in the official [documentation](https://docs.qgis.org/3.16/fr/docs/user_manual/introduction/qgis_configuration.html#deploying-qgis-within-an-organization).

OSGeo4W is the package manager used by QGIS, GRASS and most OSGeo project to provide binaries for Windows.  

QGIS, all the underlying libraries (OGR, GDAL, etc..), GRASS, SAGA, a full python environnement, Qt, etc are available in OSGeo4W.

QGIS can also be installed in its different maintained versions: LTR - Release and dev in a stable way, where the standalone installer will duplicate the whole environnement at each version. 

As OSGeo4W is a package manager, it is possible to set dependencies between applications, libraries and command line utilities. 

Installing minor upgrades is really light and simple, and thus highly recommended in a corporate environnement.

This script currently used former osgeo4W setup that was updated to V2 in june 2021. Porting is WIP. 

Thanks a lot to all the QGIS contributors, bakers and developpers that allowed to reach to target. 

# Configuring your QGIS install

A pre-configured QGIS will allow you to 

- simplify and accelerate your QGIS upgrades
- let you automate this in your favorite deployment system (OCS Inventory, SCCM, Wapt, etc...)
- control users settings, either in a strict way (proxy, authentication and connexion methods) or in a permissive way (default value but users allowed to be free)
- wire pre-installed ressources like plugins, SVG libraries, layout templates, startup project, etc...
- etc..

# How-to

## Build a OSGEO4W customization package

This recipe uses **linux shell scripts** to create the package. It is possible - though painfull - to adapt it to a Windows environnement.
However, [WSL2](https://docs.microsoft.com/en-us/windows/wsl/install-win10) may help you in building and deploying on the same machine easily. 


### Directory structure

The directory structure is standard and provided by OSGeo4W.


```
qgis-yourorganizationname/
├── apps/
│   ├── qgis-yourorganizationname/
│   │   ├── WMTS_scales.xml   -- some default scales (optional)
│   │   ├── layout_checks.py  -- some layout checks (copyright, citations, etc..) (optional)
│   │   ├── qgis-ltr-yourorganizationname.bat.template  -- .bat launcher template. This launcher will override the native qgis launchers after install
│   │   ├── qgis_constrained_settings.py  -- a nice utility to constraint some in place user settings
│   │   ├── qgis_constrained_settings.yml -- the config file to decide which settings to constrain
│   │   ├── qgis_global_settings.ini      -- your customized default settings ini file. 
│   │   ├── startup_project.qgs           -- a qgis startup project (optional)
│   │   └── qgis-ltr-backup  -- a directory to save the native OSGeo4W shortcut .lnk files that will be removed on install. Uninstall will reinstate them 
│   └── qgis-ltr/
│       └── python/
│           └── plugins/  -- Some plugins you need to deploy on the PC. 
│               ├── SpreadsheetLayers
│               ├── coordinator
│               ├── french_locator_filter
│               ├── mask
│               ├── menu_from_project
│               ├── qNote
│               └── redLayer
├── etc/
│   ├── postinstall/
│   │   └── qgis-yourorganizationname.bat  -- postinstall plugin dealing with shortcuts launchers mainly
│   └── preremove/
│       └── qgis-yourorganizationname.bat  -- preremove logic to restore a clean install when uninstalling your package
├── make.sh     -- Build your package tar.bz2 using the version tag in the setup.hint
├── deploy.sh   -- Deploy your built tar.bz2 to a local OSGeo4W repository
├── deploy_ressources_somewhere.sh  -- a demo script if you wish to deploy things on a centralized repository (optional)
└── setup.hint  -- package metadata - Change here the package name and the version only
```

### Build and deploy your package

Work on your local computer. a **linux / shell command line** is required to build the package.  

1. Play with package content
1. Increment version in setup.hint
1. Build with `./make.sh`
1. Deploy with `./deploy.sh` 
1. (uninstall) / install using either command line or OSGeo4W GUI

### Install / Uninstall your package 

This parts is run on a **Windows OS**. 

The recommended install process for organizations is to first download OSGeo4W packages and then use them for offline installs. 
This way, the GIS admin can control precisely which packages are deployed and avoid multiple downloads of ~1Go of binaries for each install.

The command line install is also the prefered way to automate your installs:

You need a powershell or classical Windows console **with elevation (ie admin) privileges**. 

_Note that the next OSGeo4W generation will allow non-admin installs._  


*Full documentation for [OSGeo4W CLI here](https://trac.osgeo.org/osgeo4w/wiki/CommandLine)*

*Below the variable names you need to change depending on your target directories choices*

```
--menu-name "WINDOWS_MENU_NAME
Ex : "OSGeo4W" , "QGIS-LTR-MonOrganisation", "QGIS"

--root "X:\OSGEO4W_DEPLOY_TEST\INSTALL" = target install directory.
Ex: "C:\OSGeo4W" , "C:\Program Files\QGIS" 

--local-package-dir "X:\OSGEO4W_DEPLOY_TEST\PAQUETS\http%3a%2f%2fwww.norbit.de%2fosgeo4w%2f"  = directory where you store your OSGeo4W binaries for offline install   
```

Examples of possible commands   

```bat

-- Install all available packages using caterogy names 

.\osgeo4w-setup.exe  --menu-name "WINDOWS_MENU_NAME" --root "X:\OSGEO4W_DEPLOY_TEST\INSTALL" --advanced  --quiet-mode --local-install --local-package-dir "X:\OSGEO4W_DEPLOY_TEST\PAQUETS\http%3a%2f%2fwww.norbit.de%2fosgeo4w%2f" --autoaccept  --delete-orphans --upgrade-also -C Libs -C Desktop -C Commandline_Utilitiesinstall

-- Uninstall only your qgis-yourorganizationname package, back to a native QGIS

.\osgeo4w-setup.exe  --menu-name "WINDOWS_MENU_NAME" --root "X:\OSGEO4W_DEPLOY_TEST\INSTALL" --advanced  --quiet-mode --local-install --local-package-dir "X:\OSGEO4W_DEPLOY_TEST\PAQUETS\http%3a%2f%2fwww.norbit.de%2fosgeo4w%2f" --autoaccept  --delete-orphans --upgrade-also -x qgis-yourorganizationname

-- Install only your package. Will also install qgis-ltr as it depends on it 

.\osgeo4w-setup.exe  --menu-name "WINDOWS_MENU_NAME" --root "X:\OSGEO4W_DEPLOY_TEST\INSTALL" --advanced  --local-install --local-package-dir "X:\OSGEO4W_DEPLOY_TEST\PAQUETS\http%3a%2f%2fwww.norbit.de%2fosgeo4w%2f" --autoaccept  --delete-orphans --upgrade-also -P qgis-yourorganizationname
 
```


### Choosing between "shared directory" and "installer embedded" approach  

You can choose to install most of the resources in the binaries install dir, OR point to a shared network location. 
You can choose for each ressource what is the best for you. 
For instance, an organisation with no shared network will embbed everything in the package. 
If you have shared disks or databases, then you can use it and it is often easier to maintain. 
BUT, in case of the need for remote / offline work, having all the resources already installed can save your butt :)  

Advantages of centralized resources:
 - Easy to maintain (just add files, edit them, done)
 - No need to launch software updates for minor configuration changes

Drawbacks:
 - Network mounts can fails. Windows "letter drive" mounts does not help (tip: use UNC paths).
 - Network latence can slow down a lot QGIS opening because of on-the-fly compilation nature of python plugins.  
 - Some shared drives can have metadata or privileges access issues causing issues with plugin's load
 
 
Tip: centralize all the resources here in this git repository and deploy them automatically when releasing a new version. 
This will let you version in one unique place and avoid issues with forgeting to version some network drive files.   

What can be centralized on shared location

- python plugins - using PYTHON_PLUGINPATH variable: can't be unistalled, take precedence over user's version (to be confirmed)
- SVG symbols - using qsettings `searchPathsForSVG`
- file `global_settings.ini`: default parameters
- startup project , layout and project templates
- python code (expressions, etc.. )

What can't be centralized currently

- Style collections and color ramps


