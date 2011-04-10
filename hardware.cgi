#!/bin/sh
#
# Hardware part of TazPanel - Devices, drivers, printing
#
# Copyright (C) 2011 SliTaz GNU/Linux - GNU gpl v3
#
echo "Content-Type: text/html"
echo ""

# Common functions from libtazpanel
. lib/libtazpanel
get_config

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel'
export TEXTDOMAIN

TITLE="- Hardware"

#
# Commands
#

case "$QUERY_STRING" in
	print*)
		echo "TODO" ;;
	*)
		#
		# Default to summary with mounted filesystem, loaded modules
		#
		xhtml_header
		debug_info
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Drivers &amp; Devices"`</h2>
	<p>`gettext "Manage your computer hardware`</p>
</div>
EOT
		echo '<pre>'
			fdisk -l | fgrep Disk
		echo '</pre>'
		echo '<h3>Filesystem usage statistics</h3>'
		echo '<pre>'
			df -h | grep ^/dev
		echo '</pre>'
		echo '<h3>Loaded kernel modules</h3>'
		# Request may be modinfo output
		case "$QUERY_STRING" in
			modinfo=*)
				mod=${QUERY_STRING#modinfo=}
				gettext "Detailed information for module:"; echo " $mod"
				echo '<pre>'
				modinfo $mod
				echo '</pre>' ;;
			rmmod=*)
				mod=${QUERY_STRING#rmmod=}
				modprobe -r $mod ;;
		esac
		cat << EOT
	`table_start`
		<tr class="thead">
			<td>`gettext "Module"`</td>
			<td>`gettext "Size"`</td>
			<td>`gettext "Used"`</td>
			<td>`gettext "by"`</td>
		</tr>
EOT
		# Get the list of modules and link to modinfo
		lsmod | grep ^[a-z] | while read MOD SIZE USED BY
		do
			cat << EOT
		<tr>
			<td><a href="$SCRIPT_NAME?modinfo=$MOD">$MOD</a></td>
			<td>$SIZE</td>
			<td>$USED</td>
			<td>`echo $BY | sed s/","/" "/g`</td>
		</tr>
EOT
		done
		table_end
		echo '<h3>lspci</h3>'
		echo '<pre>'
			lspci
		echo '</pre>'
		;;
esac

xhtml_footer
exit 0
