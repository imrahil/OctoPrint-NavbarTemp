# coding=utf-8
import setuptools

########################################################################################################################

plugin_identifier = "navbartemp"
plugin_package = "octoprint_%s" % plugin_identifier
plugin_name = "OctoPrint-NavbarTemp"
plugin_version = "0.14"
plugin_description = "Displays temperatures on navbar"
plugin_author = "Jarek Szczepanski & Cosik"
plugin_author_email = "imrahil@imrahil.com & cosik3d@gmail.com"
plugin_url = "https://github.com/imrahil/OctoPrint-NavbarTemp"
plugin_license = "AGPLv3"
plugin_additional_data = ['libs']

########################################################################################################################

def package_data_dirs(source, sub_folders):
	import os
	dirs = []

	for d in sub_folders:
		folder = os.path.join(source, d)
		if not os.path.exists(folder):
			continue

		for dirname, _, files in os.walk(folder):
			dirname = os.path.relpath(dirname, source)
			for f in files:
				dirs.append(os.path.join(dirname, f))

	return dirs

def params():
	# Our metadata, as defined above
	name = plugin_name
	version = plugin_version
	description = plugin_description
	author = plugin_author
	author_email = plugin_author_email
	url = plugin_url
	license = plugin_license

	# we only have our plugin package to install
	packages = [plugin_package]

	# we might have additional data files in sub folders that need to be installed too
	package_data = {plugin_package: package_data_dirs(plugin_package, ['static', 'templates', 'translations'] + plugin_additional_data)}
	include_package_data = True

	# If you have any package data that needs to be accessible on the file system, such as templates or static assets
	# this plugin is not zip_safe.
	zip_safe = False

	# Requirements
	install_requires = ['OctoPrint']

    # Additional requirements for optional install options and/or OS-specific dependencies
	extras_require = {
			# Dependencies for development
			"develop": [
				# Testing dependencies
				"ddt",
				"mock>=4,<5",
				"pytest-doctest-custom>=1.0.0,<2",
				"pytest>=6.2.5,<7",
				# pre-commit
				"pre-commit",
				# profiler
				"pyinstrument",
				],
			}

	# Hook the plugin into the "octoprint.plugin" entry point, mapping the plugin_identifier to the plugin_package.
	# That way OctoPrint will be able to find the plugin and load it.
	entry_points = {
		"octoprint.plugin": ["%s = %s" % (plugin_identifier, plugin_package)]
	}

	return locals()

setuptools.setup(**params())
