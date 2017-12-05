$(function() {
    function NavbarTempViewModel(parameters) {
        var self = this;

        self.navBarTempModel = parameters[0];
        self.global_settings = parameters[1];
        self.raspiTemp = ko.observable();
        self.isRaspi = ko.observable(false);

        self.formatBarTemperature = function(toolName, actual, target) {
            var output = toolName + ": " + _.sprintf("%.1f&deg;C", actual);

            if (target) {
                var sign = (target >= actual) ? " \u21D7 " : " \u21D8 ";
                output += sign + _.sprintf("%.1f&deg;C", target);
            }

            return output;
        };

        self.onBeforeBinding = function () {
            self.settings = self.global_settings.settings.plugins.navbartemp;
        };

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "navbartemp") {
                return;
            }

            if (!data.hasOwnProperty("israspi")) {
                self.isRaspi(false);
                return;
            } else {
                self.isRaspi(true);
            }

            self.raspiTemp(_.sprintf("Raspi: %.1f&deg;C", data.raspitemp));
        };
    }

    ADDITIONAL_VIEWMODELS.push([
        NavbarTempViewModel, 
        ["temperatureViewModel", "settingsViewModel"],
        ["#navbar_plugin_navbartemp", "#settings_plugin_navbartemp"]
    ]);
});
