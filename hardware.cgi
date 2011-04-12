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
	modules*|modinfo=*)
		query_string_parser
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
		case "$QUERY_STRING" in
			modinfo=*)
				echo '<strong>'
				gettext "Detailed information for module: "; echo "$WANT"
				echo '</strong>'
				echo '<pre>'
				modinfo $WANT
				echo '</pre>' ;;
			modprobe=*)
				echo '<pre>'
				modprobe -v $WANT
				echo '</pre>' ;;
			rmmod=*)
				#modprobe -r $WANT
				echo "Removing"
				rmmod -w $WANT ;;
			*search=*)
				gettext "Matching result(s) for: "; echo "$VAR_1"
				echo '<pre>'
				modprobe -l | grep "$VAR_1" | while read line
				do
					name=$(basename $line)
					mod=${name%.ko.gz}
					echo "Module    : <a href='$SCRIPT_NAME?modinfo=$mod'>$mod</a> "
				done
				echo '</pre>' ;;
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
	<a class="button" href="$SCRIPT_NAME?modules">Kernel modules</a>
</div>
EOT
		echo '<h3>Filesystem usage statistics</h3>'
		echo '<pre>'
			fdisk -l | fgrep Disk
		echo '</pre>'
		echo '<pre>'
			df -h | grep ^/dev
		echo '</pre>'		
		echo '<h3>lspci</h3>'
		echo '<pre>'
			lspci -k
		echo '</pre>'
		echo '<h3>lsusb</h3>'
		echo '<pre>'
			lsusb
		echo '</pre>'
		;;
esac

xhtml_footer
exit 0
