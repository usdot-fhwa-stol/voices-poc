## Install Multiple SPaT Plugins
In order to collect SPaT messages from multiple traffic controllers in V2X Hub, a SPaT plugin for each controller must be used. The easiest way to accomplish this is to create a zipped plugin package for each intersection and install them into the V2X Hub. The plugin package contains the SPaT plugin executable and a customized manifest.json file contained in a uniquely named folder (ex: SpatPlugin_East). These zipped packages are then copied into the V2X Hub docker container and installed using the command: 

`tmxctl --plugin-install <plugin_package>.zip`

At TFHRC, we have an East and West intersection so a zipped installation package for both intersections was created as well as a script which automatically checks for an existing zipped package then copies and installs them if they are not found. 

NOTE: This script assumes the name of the v2xhub image is `v2xhub`.

## Install Multiple tenaspatplugins
Each SPaT plugin needs its own tenaspatplugin to create TENA SDOs. This is accomplished by copying the resulting build directory from the buildTenaAdapter.sh script for each requred tenaspatplugin. For example, TFHRC requires a tenaspatplugin for its East and West intersections so a `build_east` and `build_west` copy were created. 

Once the directories are created, a customized manifest.json must be placed in the `build/bin` directory (ex: `build_east/bin/manifest.json`). Files for the TFHRC East and West intersections are included but source file can be found at `tenaspatplugin/TenaSpatPlugin/manifest.json`.

NOTE: These files must be named exactly `manifest.json` when placed in the `build/bin` directory.
