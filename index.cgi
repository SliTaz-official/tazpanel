#!/bin/sh
#
# Main CGI interface for TazPanel. In on word: KISS. Use the main cas form
# command so we are faster and dont load unneeded function. If nececarry
# you can use the lib/ dir to handle external resources.
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

#
# Commands
#

case "$QUERY_STRING" in
	boot)
		#
		# Everything until user login
		#
		. /etc/rcS.conf
		TITLE="- Boot"
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Boot &amp; startup"`</h2>
	<p>
		`gettext "Everything that appends before user login."` 
	</p>
</div>

<h3>`gettext "Kernel cmdline"`</h3>
<pre>
`cat /proc/cmdline`
</pre>

<h3>`gettext "Local startup commands"`</h3>
<pre>
`cat /etc/init.d/local.sh`
</pre>

EOT
		;;
	hardware|modinfo=*)
		#
		# Hardware drivers, devices, filesystem, screen
		#
		TITLE="- Hardware"
		xhtml_header
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
		# We may want modinfi output
		
		case "$QUERY_STRING" in
			modinfo=*)
				mod=${QUERY_STRING#modinfo=}
				gettext "Detailled information for module:"; echo " $mod"
				echo '<pre>'
				modinfo $mod
				echo '</pre>' ;;
			rmmod=*)
				mod=${QUERY_STRING#rmmod=}
				modprobe -r $mod ;;
		esac
		table_start
		cat << EOT
<tr class="thead">
	<td>`gettext "Module"`</td>
	<td>`gettext "Size"`</td>
	<td>`gettext "Used"`</td>
	<td>`gettext "by"`</td>
</tr>
EOT
		# Get the list of modules and link to modinfo
		lsmod | grep ^[a-z] | while read line
		do
			mod=`echo "$line" | awk '{print $1}'`
			echo '<tr>'
			echo "<td><a href='$SCRIPT_NAME?modinfo=$mod'>$mod</a></td>"
			echo "$line" | awk '{print "<td>", $2, "</td>",
				"<td>", $3, "</td>", "<td>", $4, "</td>"}'
			echo '</tr>'
		done
		table_end
		echo '<h3>lspci</h3>'
		echo '<pre>'
			lspci
		echo '</pre>'
		;;
	*)
		#
		# Default xHTML content
		#
		xhtml_header
		case "$QUERY_STRING" in
			gen-locale=*)
				new_locale=${QUERY_STRING#gen-locale=} ;;
			rdate)
				echo "" ;;
		esac
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Host:"` `hostname`</h2>
	<p>`gettext "SliTaz administration et configuration Panel"`<p>
</div>

<h3>`gettext "Summary"`</h3>
<div id="summary">
	<p>
		`gettext "Uptime:"` `uptime`
	</p>
	<p>
		`gettext "Memory in Mb"`
		`free -m | grep Mem: | awk \
		'{print "| Total:", $2, "| Used:", $3, "| Free:", $4}'`
	</p>
<!-- Close summary -->
</div>

<h4>`gettext "Network status"`</h4>
`list_network_interfaces`

<h4>`gettext "Filesystem usage statistics"`</h4>
<pre>
`df -h | grep ^/dev`
</pre>
EOT
		;;
esac

xhtml_footer
exit 0
