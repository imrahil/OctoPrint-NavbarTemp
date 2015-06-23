$(function() {
    function NavbarTempViewModel(parameters) {
        var self = this;

        self.navBarTempModel = parameters[0];
        self.raspiTemp = ko.observable();
        self.isRaspi = ko.observable(false);

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
        ["temperatureViewModel"], 
        ["#navbar_plugin_navbartemp"]
    ]);
});

function formatBarTemperature(toolName, actual, target) {
    var output = toolName + ": " + _.sprintf("%.1f&deg;C", actual);

    if (target) {
        output += " \u21D7 " + _.sprintf("%.1f&deg;C", target);
    }

    return output;
};
