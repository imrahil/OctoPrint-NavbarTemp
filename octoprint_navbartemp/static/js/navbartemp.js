$(function() {
    function NavbarTempViewModel(parameters) {
        var self = this;

        self.navBarTempModel = parameters[0];
    }

    ADDITIONAL_VIEWMODELS.push([
        NavbarTempViewModel, 
        ["temperatureViewModel"], 
        ["#navbar_plugin_navbartemp"]
    ]);
});

function formatBarTemperature(actual, target) {
    var output = _.sprintf("%.1f&deg;C", actual);

    if (target) {
        output += " \u21D7 " + _.sprintf("%.1f&deg;C", target);
    }

    return output;
}
