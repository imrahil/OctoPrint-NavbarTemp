# coding=utf-8
from __future__ import absolute_import

__author__ = "Jarek Szczepanski <imrahil@imrahil.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2014 Jarek Szczepanski - Released under terms of the AGPLv3 License"

import octoprint.plugin
from octoprint.util import RepeatedTimer
import sys
import re

class NavBarPlugin(octoprint.plugin.StartupPlugin,
                   octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.SettingsPlugin):

    def __init__(self):
        self.isRaspi = False
        self.isOdroidXU3 = False
        self.debugMode = False      # to simulate temp on Win/Mac
        self.displayRaspiTemp = True
        self.displayOdroidXU3Temp = True
        self._checkTempTimer = None

    def on_after_startup(self):
        self.displayRaspiTemp = self._settings.get(["displayRaspiTemp"])
        self.displayOdroidXU3Temp = self._settings.get(["displayOdroidXU3Temp"])
        self._logger.debug("displayRaspiTemp: %s, displayOdroidXU3Temp: %s" % (self.displayRaspiTemp, self.displayOdroidXU3Temp))

        if sys.platform == "linux2":
            with open('/proc/cpuinfo', 'r') as infile:
                    cpuinfo = infile.read()
            # Match a line like 'Hardware   : BCM2709'
            match = re.search('^Hardware\s+:\s+([a-zA-Z0-9_-]+)$', cpuinfo, flags=re.MULTILINE | re.IGNORECASE)

            if match is None:
                # Couldn't find the hardware, assume it isn't a pi.
                self.isRaspi = False
                self.isOdroidXU3 = False
            elif match.group(1) == 'BCM2708':
                self._logger.debug("Pi 1")
                self.isRaspi = True
                self.isOdroidXU3 = False
            elif match.group(1) == 'BCM2709':
                self._logger.debug("Pi 2")
                self.isRaspi = True
                self.isOdroidXU3 = False
            elif match.group(1) == 'ODROID-XU3':
                self._logger.debug("Odroid XU3")
                self.isRaspi = False
                self.isOdroidXU3 = True

            if (self.isRaspi and self.displayRaspiTemp) or (self.isOdroidXU3 and self.displayOdroidXU3Temp):
                self._logger.debug("Let's start RepeatedTimer!")
                self.startTimer(30.0)
        elif self.debugMode:
            self.isRaspi = True
            self.isOdroidXU3 = True
            if self.displayRaspiTemp or self.displayOdroidXU3Temp:
                self.startTimer(5.0)

        self._logger.debug("is Raspberry Pi? - %s, is Odroid XU3? - %s" % (self.isRaspi, self.isOdroidXU3))

    def startTimer(self, interval):
        if self.isRaspi:
            self._checkTempTimer = RepeatedTimer(interval, self.checkRaspiTemp, None, None, True)
        elif self.isOdroidXU3:
            self._checkTempTimer = RepeatedTimer(interval, self.checkOdroidXU3Temp, None, None, True)
        self._checkTempTimer.start()

    def checkRaspiTemp(self):
        from sarge import run, Capture

        self._logger.debug("Checking Raspberry Pi internal temperature")

        if sys.platform == "linux2":
            p = run("/opt/vc/bin/vcgencmd measure_temp", stdout=Capture())
            p = p.stdout.text

        elif self.debugMode:
            import random
            def randrange_float(start, stop, step):
                return random.randint(0, int((stop - start) / step)) * step + start
            p = "temp=%s'C" % randrange_float(5, 60, 0.1)

        self._logger.debug("response from sarge: %s" % p)

        match = re.search('=(.*)\'', p)
        if not match:
            self.isRaspi = False
        else:
            temp = match.group(1)
            self._logger.debug("match: %s" % temp)
            self._plugin_manager.send_plugin_message(self._identifier, dict(israspi=self.isRaspi, raspitemp=temp))

    def checkOdroidXU3Temp(self):
        from sarge import run, Capture

        self._logger.debug("Checking Odroid XU3 internal temperature")

        if sys.platform == "linux2":
            p = run("cat /sys/devices/virtual/thermal/thermal_zone0/temp", stdout=Capture())
            p = p.stdout.text

        elif self.debugMode:
            import random
            def randrange_float(start, stop, step):
                return random.randint(0, int((stop - start) / step)) * step + start
            p = "temp=%s'C" % randrange_float(5, 60, 0.1)

        self._logger.debug("response from sarge: %s" % p)

        match = re.search('(\d+)', p)
        if not match:
            self.isOdroidXU3 = False
        else:
            temp = str(int(match.group(1)) / 1000.0)
            self._logger.debug("match: %s" % temp)
            self._plugin_manager.send_plugin_message(self._identifier, dict(isodroidxu3=self.isOdroidXU3, odroidxu3temp=temp))

	##~~ SettingsPlugin
    def get_settings_defaults(self):
        if self.isRaspi or self.isOdroidXU3:
            return dict(displayRaspiTemp = self.displayRaspiTemp, displayOdroidXU3Temp = self.displayOdroidXU3Temp)

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        self.displayRaspiTemp = self._settings.get(["displayRaspiTemp"])
        self.displayOdroidXU3Temp = self._settings.get(["displayOdroidXU3Temp"])

        if self.displayRaspiTemp or self.displayOdroidXU3Temp:
            interval = 5.0 if self.debugMode else 30.0
            self.startTimer(interval)
        else:
            if self._checkTempTimer is not None:
                try:
                    self._checkTempTimer.cancel()
                except:
                    pass
            self._plugin_manager.send_plugin_message(self._identifier, dict())

	##~~ TemplatePlugin API
    def get_template_configs(self):
        if self.isRaspi or self.isOdroidXU3:
            return [
                dict(type="settings", template="navbartemp_settings.jinja2")
            ]
        else:
            return []

    ##~~ AssetPlugin API
    def get_assets(self):
        return {
            "js": ["js/navbartemp.js"],
            "css": ["css/navbartemp.css"],
            "less": ["less/navbartemp.less"]
        }

    ##~~ Softwareupdate hook
    def get_update_information(self):
        return dict(
            navbartemp=dict(
                displayName="Navbar Temperature Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="imrahil",
                repo="OctoPrint-NavbarTemp",
                current=self._plugin_version,

                # update method: pip w/ dependency links
                pip="https://github.com/imrahil/OctoPrint-NavbarTemp/archive/{target_version}.zip"
            )
        )

__plugin_name__ = "Navbar Temperature Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = NavBarPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
