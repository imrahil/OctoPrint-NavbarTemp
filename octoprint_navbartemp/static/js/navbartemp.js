$(function() {
    function NavbarTempViewModel(parameters) {
        var self = this;

        self.temperatureModel = parameters[0];
        self.global_settings = parameters[1];
        self.socTemp = ko.observable(null);
        self.custCmd = ko.observable(null);
        /*
         * raspi and awinner should be combined into something like hasSoc in the python
         * source, there's no need for this part to know or care what the sbc is made of
         *
         */
        self.isSupported = ko.observable();
        //hassoc should be taken care of in the python source before it gets this far
        self.hasSoc = ko.pureComputed(function() {
            return self.isSupported;
        });

        self.onBeforeBinding = function () {
            self.settings = self.global_settings.settings.plugins.navbartemp;
            console.log(self.settings);
        };

        self.formatBarTemperature = function(toolName, actual, target) {
            if(self.settings.useShortNames()) {
                var name = toolName.charAt(0);
                if(toolName.split(" ")[1]) {
                    name += toolName.split(" ")[1];
                }else {
                    name += "0";
                }
            } else {
                var name = toolName;
            }
            var output = name + ": " + _.sprintf("%.1f&deg;C", actual);

            if (target) {
                var sign = (target >= actual) ? " \u21D7 " : " \u21D8 ";
                output += sign + _.sprintf("%.1f&deg;C", target);
            }
            return output;
        };

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "navbartemp") {
                return;
            }

            var output = ""
            if (data.soctemp) {
                output = _.sprintf("SoC: %.1f&deg;C", data.soctemp);
            }
            if (data.cmd_name) {
                output +=  _.sprintf(" %s: ", data.cmd_name) + _.sprintf("%s",data.cmd_result);
            }
            self.socTemp(_.sprintf(output));
        };

    }

    OCTOPRINT_VIEWMODELS.push({
        construct: NavbarTempViewModel,
        dependencies: ["temperatureViewModel", "settingsViewModel"],
        elements: ["#navbar_plugin_navbartemp", "#settings_plugin_navbartemp"]
    });
});
