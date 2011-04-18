#!/bin/sh
#
# Hardware part of TazPanel - Devices, drivers, printing
#
# Copyright (C) 2011 SliTaz GNU/Linux - BSD License
#

# Common functions from libtazpanel
. lib/libtazpanel
get_config
header

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel'
export TEXTDOMAIN

TITLE="- Hardware"

#
# Commands
#

case " $(GET) " in
	*\ print\ *)
		echo "TODO" ;;
	*\ modules\ *|*\ modinfo\ *)
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Kernel modules"`</h2>
<div class="float-right">
	<form method="get" action="$SCRIPT_NAME">
		<input type="hidden" name="modules" />
		<input type="text" name="search" />
	</form>
</div>
	<p>`gettext "Manage, search or get information about the Linux kernel modules`</p>
</div>
EOT
		# Request may be modinfo output that we want in the page itself
		if [ -n "$(GET modinfo)" ]; then
			echo '<strong>'
			gettext "Detailed information for module: "; echo "$(GET modinfo)"
			echo '</strong>'
			echo '<pre>'
			modinfo $(GET modinfo)
			echo '</pre>'
		fi
		if [ -n "$(GET modprobe)" ]; then
			echo '<pre>'
			modprobe -v $(GET modprobe)
			echo '</pre>' 
		fi
		if [ -n "$(GET rmmod)" ]; then
			echo "Removing"
			rmmod -w $(GET rmmod)
		fi
		if [ -n "$(GET search)" ]; then
			gettext "Matching result(s) for: "; echo "$(GET search)"
			echo '<pre>'
			modprobe -l | grep "$(GET search)" | while read line
			do
				name=$(basename $line)
				mod=${name%.ko.gz}
				echo "Module    : <a href='$SCRIPT_NAME?modinfo=$mod'>$mod</a> "
			done
			echo '</pre>'
		fi
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
		table_end ;;
	*)
		#
		# Default to summary with mounted filesystem, loaded modules
		#
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Drivers &amp; Devices"`</h2>
	<p>`gettext "Manage your computer hardware`</p>
</div>
<div>
	<a class="button" href="$SCRIPT_NAME?modules">
		<img src="$IMAGES/tux.png" />Kernel modules</a>
</div>

<h3>$(gettext "Filesystem usage statistics")</h3>
<pre>
EOT
		fdisk -l | fgrep Disk
		echo '</pre>'
		echo '<pre>'
			df -h | grep ^/dev
		echo '</pre>'
		echo "<h3>$(gettext "System memory")</h3>"
		echo '<pre>'
		free -m | sed \
			-e s"#total.*\([^']\)#<span class='top'>\0</span>#"g \
			-e s"#^[A-Z-].*:\([^']\)#<span class='sh-comment'>\0</span>#"g
		echo '</pre>'
		echo '<h3>lspci</h3>'
		echo '<pre>'
			lspci -k | \
				sed s"#^[0-9].*\([^']\)#<span class='diff-at'>\0</span>#"g
		echo '</pre>'
		echo '<h3>lsusb</h3>'
		echo '<pre>'
			lsusb
		echo '</pre>'
		;;
esac

xhtml_footer
exit 0
