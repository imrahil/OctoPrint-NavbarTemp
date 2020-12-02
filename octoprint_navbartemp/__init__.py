# coding=utf-8
from __future__ import absolute_import

__author__ = "Jarek Szczepanski <imrahil@imrahil.com>  & Cosik <cosik3d@gmail.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2014 Jarek Szczepanski - Released under terms of the AGPLv3 License"

import octoprint.plugin
from octoprint.util import RepeatedTimer
import sys
import os

from .libs.sbc import SBCFactory, SBC


class NavBarPlugin(octoprint.plugin.StartupPlugin,
                   octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.SettingsPlugin):

    def __init__(self):
        # Array of raspberry pi SoC's to check against, saves having a large if/then statement later
        self.piSocTypes = (["BCM2708", "BCM2709", "BCM2835", "BCM2711"])
        self.debugMode = False  # to simulate temp on Win/Mac
        self.displayRaspiTemp = None
        self._checkTempTimer = None
        self._checkCmdTimer = None
        self.sbc = SBC()
        self.cmd = None
        self.cmd_name = None

    def on_after_startup(self):
        self.displayRaspiTemp = self._settings.get(["displayRaspiTemp"])
        self.piSocTypes = self._settings.get(["piSocTypes"])
        self.cmd = self._settings.get(["cmd"])
        self.cmd_name = self._settings.get(["cmd_name"])
        self._logger.debug("Custom cmd name %r" % self.cmd_name)
        self._logger.debug("Custom cmd %r" % self.cmd)

        if sys.platform.startswith("linux"):
            self.sbc = SBCFactory().factory(self._logger)
            if self.debugMode:
                self.sbc.is_supported = True
                self.sbc.debugMode = True
            if self.sbc.is_supported and self.displayRaspiTemp:
                self._logger.debug("Let's start RepeatedTimer!")
                interval = 5.0 if self.debugMode else 30.0
                self.start_soc_timer(interval)

        if self.cmd_name:
            interval = 5.0 if self.debugMode else 30.0
            self.start_custom_timer(interval)

        try:
            self._logger.debug("is supported? - %s" % self.sbc.is_supported)
        except Exception:
            self._logger.debug("Embeded platform is not detected")

    def start_soc_timer(self, interval):
        self._checkTempTimer = RepeatedTimer(interval, self.update_soc_temp, run_first=True)
        self._checkTempTimer.start()

    def start_custom_timer(self, interval):
        self._checkCmdTimer = RepeatedTimer(interval, self.update_custom, run_first=True)
        self._checkCmdTimer.start()

    def update_soc_temp(self):
        temp = self.sbc.check_soc_temp()
        self._logger.debug("match: %s" % temp)
        self._plugin_manager.send_plugin_message(self._identifier,
                                                 dict(isSupported=self.sbc.is_supported,
                                                      soctemp=temp))

    def update_custom(self):
        cmd_rtv = self.get_custom_result()
        self._plugin_manager.send_plugin_message(self._identifier,
                                                 dict(cmd_result=cmd_rtv, cmd_name=self.cmd_name))

    def get_custom_result(self):
        if self.cmd:
            try:
                cmd_rtv = str(os.popen(self.cmd).read())
                self._logger.debug("cmd_rtv: %s" % cmd_rtv)
                return cmd_rtv
            except Exception:
                self._logger.debug("cmd error")
                return ""

    # ~~ SettingsPlugin
    def get_settings_defaults(self):
        return dict(displayRaspiTemp=True,
                    piSocTypes=self.piSocTypes,
                    cmd="",
                    cmd_name="",
                    useShortNames=False,
                    makeMoreRoom=False,
                    soc_name="SoC",
                    )

    def on_settings_save(self, data):
        diff = super(NavBarPlugin, self).on_settings_save(data)
        self._logger.debug("data: " + str(data))

        if "displayRaspiTemp" in data:
            self.displayRaspiTemp = data["displayRaspiTemp"]
            if self.displayRaspiTemp:
                interval = 5.0 if self.debugMode else 30.0
                self.start_soc_timer(interval)
            else:
                if self._checkTempTimer is not None:
                    try:
                        self._checkTempTimer.cancel()
                    except Exceptionx:
                        pass
        if "cmd" in data:
            self.cmd = data["cmd"]
            self.cmd_name = data["cmd_name"]
            if self.cmd:
                interval = 5.0 if self.debugMode else 30.0
                self.start_custom_timer(interval)
            else:
                if self._checkCmdTimer is not None:
                    try:
                        self._checkCmdTimer.cancel()
                    except Exceptionx:
                        pass
        self._plugin_manager.send_plugin_message(self._identifier, dict())

        return diff

    # ~~ TemplatePlugin API
    def get_template_configs(self):
        try:
            # Todo: settings have to be fixed
            # if self.sbc.is_supported:
            #     return [
            #         dict(type="settings", template="navbartemp_settings_sbc.jinja2")
            #     ]
            # else:
            return [dict(type="settings", template="navbartemp_settings.jinja2")]
        except Exception:
            return []

    # ~~ AssetPlugin API
    def get_assets(self):
        return {
            "js": ["js/navbartemp.js"],
            "css": ["css/navbartemp.css"],
            "less": ["less/navbartemp.less"]
        }

    # ~~ Softwareupdate hook
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
__plugin_author__ = "Jarek Szczepanski & Cosik"
__plugin_url__ = "https://github.com/imrahil/OctoPrint-NavbarTemp"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now.
__plugin_pythoncompat__ = ">=2.7,<4"  # python 2 and 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = NavBarPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
