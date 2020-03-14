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
v 0.14 
- Temperature is visible, connection is no needed #47 #65
- Fix for python 3 - #68  
- Support for shorter tool names - #29

v 0.13 
- added support for custom commands  

v 0.11 
- added support for all platforms running under Armbian  