# coding=utf-8
from __future__ import absolute_import

__author__ = "Jarek Szczepanski <imrahil@imrahil.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2014 Jarek Szczepanski - Released under terms of the AGPLv3 License"

import octoprint.plugin
from octoprint.util import RepeatedTimer
import sys
import re

from .libs.sbc import SBCFactory


class NavBarPlugin(octoprint.plugin.StartupPlugin,
                   octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.SettingsPlugin):

    def __init__(self):
        self.piSocTypes = (["BCM2708", "BCM2709",
                            "BCM2835"])  # Array of raspberry pi SoC's to check against, saves having a large if/then statement later
        self.debugMode = False  # to simulate temp on Win/Mac
        self.displayRaspiTemp = True
        self._checkTempTimer = None
        self.sbc = None

    def on_after_startup(self):
        self.displayRaspiTemp = self._settings.get(["displayRaspiTemp"])
        self.piSocTypes = self._settings.get(["piSocTypes"])
        self._logger.debug("displayRaspiTemp: %s" % self.displayRaspiTemp)

        if sys.platform == "linux2":
            self.sbc = SBCFactory().factory(self._logger)

            if self.sbc.is_supported and self.displayRaspiTemp:
                self._logger.debug("Let's start RepeatedTimer!")
                self.startTimer(30.0)
        # debug mode doesn't work if the OS is linux on a regular pc
        elif self.debugMode:
            self.sbc.is_supported = True
            if self.displayRaspiTemp:
                self.startTimer(5.0)

        self._logger.debug("is supported? - %s" % self.sbc.is_supported)

    def startTimer(self, interval):
        self._checkTempTimer = RepeatedTimer(interval, self.updateSoCTemp, None, None, True)
        self._checkTempTimer.start()

    def updateSoCTemp(self):
        temp = self.sbc.checkSoCTemp()
        self._logger.debug("match: %s" % temp)
        self._plugin_manager.send_plugin_message(self._identifier,
                                                 dict(isSupported=self.sbc.is_supported,
                                                      soctemp=temp))

    ##~~ SettingsPlugin
    def get_settings_defaults(self):
        return dict(displayRaspiTemp=self.displayRaspiTemp,
                    piSocTypes=self.piSocTypes)

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        self.displayRaspiTemp = self._settings.get(["displayRaspiTemp"])

        if self.displayRaspiTemp:
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
        if self.sbc.is_supported:
            return [
                dict(type="settings", template="navbartemp_settings_raspi.jinja2")
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


__plugin_name__ = "Navbar Temperature Plugin (ntoff mod)"
__plugin_author__ = "Jarek Szczepanski (modified by ntoff)"
__plugin_url__ = "https://github.com/ntoff/OctoPrint-NavbarTemp"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = NavBarPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }