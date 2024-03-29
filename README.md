# Plugin for OctoPrint - displays temperatures on navbar

![NavbarTemp](images/navbar.png?raw=true)


## Setup

Install the plugin using Plugin Manager from Settings

## Need new platform support?
If you need support for additional platform, please inform us and add such information:
* How to read temperature
* How to define platform type

And be ready for testing.

## Custom command
Plugin is supporting up to one custom command, in navbar will be displayed raw output
of command.
Example:
![NavbarTemp](images/custom_cmd_cfg1.png?raw=true)

![NavbarTemp](images/custom_cmd_bar1.png?raw=true)


## Change notes:
v 0.15
- Fix few exceptions
- Themify support added Also made the CSS safe from conflicting with other elements
- Hide tools temps when not active https://github.com/imrahil/OctoPrint-NavbarTemp/issues/80
- Fahrenheit display added https://github.com/imrahil/OctoPrint-NavbarTemp/issues/63 https://github.com/imrahil/OctoPrint-NavbarTemp/issues/37
- Add BCM2711 as supported SoC
- Consolidate vcgencmd path between versions

v 0.14
- Temperature is visible, connection is no needed #47 #65
- Fix for python 3 - #68
- Support for shorter tool names - #29
- Fix for settings saving reported in #47
- Added possibility to remove target temperature output #57
- Added possibility to configure soc name on navbar  #43

v 0.13
- added support for custom commands

v 0.11
- added support for all platforms running under Armbian
