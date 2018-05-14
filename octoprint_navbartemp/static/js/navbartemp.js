$(function() {
    function NavbarTempViewModel(parameters) {
        var self = this;

        self.navBarTempModel = parameters[0];
        self.global_settings = parameters[1];
        self.raspiTemp = ko.observable();
        self.isRaspi = ko.observable(false);

        self.formatBarTemperature = function(toolName, actual, target) {
            var displayName = "";
            
            if (toolName == "Tool" || toolName == "End" || toolName == "Hotend" || toolName == "Hot End") {
                displayName = self.settings.displayNames.hotend;
            } else if (toolName == "Bett" || toolName == "Bed") {
                displayName = self.settings.displayNames.bed;
            } else {
               displayName = toolName + ":";
            }
            
            var output = _.sprintf("%s %.1f&deg;C", displayName, actual);

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

            self.raspiTemp(_.sprintf("%s %.1f&deg;C", self.settings.displayNames.raspi, data.raspitemp));
        };
    }

    ADDITIONAL_VIEWMODELS.push([
        NavbarTempViewModel, 
        ["temperatureViewModel", "settingsViewModel"],
        ["#navbar_plugin_navbartemp", "#settings_plugin_navbartemp"]
    ]);
});
