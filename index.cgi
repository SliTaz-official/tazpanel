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
