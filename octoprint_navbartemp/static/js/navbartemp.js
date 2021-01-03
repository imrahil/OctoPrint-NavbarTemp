$(function() {
    function NavbarTempViewModel(parameters) {
        var self = this;

        self.temperatureModel = parameters[0];
        self.global_settings = parameters[1];
        self.socTemp = ko.observable("");
        self.custCmd = ko.observable("");
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

        self.onAllBound = function(){
            // Check for themify - sadly the themeify plugin always sets the "themeify" class on html even though themes are not active so we cant use that as not selector in the css - so we use js :(
            if (OctoPrint.coreui.viewmodels.settingsViewModel.settings.plugins.hasOwnProperty('themeify')){
                OctoPrint.coreui.viewmodels.settingsViewModel.settings.plugins.themeify.enabled.subscribe(function(enabled) {
                    if (enabled){
                        $('#navbar_plugin_navbartemp').removeClass('ThemeifyOff');
                    }else{
                        $('#navbar_plugin_navbartemp').addClass('ThemeifyOff');
                    }
                });
                if (!OctoPrint.coreui.viewmodels.settingsViewModel.settings.plugins.themeify.enabled()){
                    $('#navbar_plugin_navbartemp').addClass('ThemeifyOff');
                }
            }else{
                $('#navbar_plugin_navbartemp').addClass('ThemeifyOff');
            }
        }

        self.onBeforeBinding = function () {
            self.settings = self.global_settings.settings.plugins.navbartemp;
        };

        self.formatBarTemperature = function(toolName, actual, target) {
            if(self.settings.useShortNames() == true) {
                var name = toolName.charAt(0);
                if(name == 'T'){
                    name = 'E';
                }
                if(toolName.split(" ")[1]) {
                    name += toolName.split(" ")[1];
                }
            } else {
                var name = toolName;
            }
            var output = ""

            if(self.settings.makeMoreRoom() == false) {
                output = name + ": " + _.sprintf("%.1f&deg;C", actual);
                if (target) {
                    var sign = (target >= actual) ? " \u21D7 " : " \u21D8 ";
                    output += sign + _.sprintf("%.1f&deg;C", target);
                }
            } else {
                output = name + ":" + _.sprintf("%.1f&deg;C", actual);
            }
            // Add fahrenheit
            if (OctoPrint.coreui.viewmodels.settingsViewModel.appearance_showFahrenheitAlso()){
                output += " ("+_.sprintf("%.1f&deg;F", (actual * (9/5)) + 32)+")";
            }
            return output;
        };

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "navbartemp") {
                return;
            }

            if (data.soctemp) {
                // Add fahrenheit
                var fahrenheit = '';
                if (OctoPrint.coreui.viewmodels.settingsViewModel.appearance_showFahrenheitAlso()){
                    fahrenheit = " ("+_.sprintf("%.1f&deg;F", (data.soctemp * (9/5)) + 32)+")";
                }
                if(self.settings.makeMoreRoom() == false) {
                    self.socTemp(self.settings.soc_name() + _.sprintf(": %.1f&deg;C", data.soctemp)+fahrenheit);
                } else {
                    self.socTemp(self.settings.soc_name() + _.sprintf(":%.1f&deg;C", data.soctemp)+fahrenheit);
                }
            }
            if (data.cmd_name) {
                self.custCmd( _.sprintf(" %s: ", data.cmd_name) + _.sprintf("%s",data.cmd_result));
            }
        };

        self.onSettingsHidden = function () {
            if(self.settings.displayRaspiTemp() == false) {
                self.socTemp("");
            }
        };

    }

    OCTOPRINT_VIEWMODELS.push({
        construct: NavbarTempViewModel,
        dependencies: ["temperatureViewModel", "settingsViewModel"],
        elements: ["#navbar_plugin_navbartemp", "#settings_plugin_navbartemp"]
    });
});
