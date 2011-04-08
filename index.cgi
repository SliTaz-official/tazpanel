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
# Things to do before displaying the page
#

case "$QUERY_STRING" in
	panel-pass=*)
		new=${QUERY_STRING#*=}
		sed -i s@/:root:.*@/:root:$new@ $HTTPD_CONF ;;
	*) continue ;;
esac

#
# Commands
#

case "$QUERY_STRING" in
	*)
		#
		# Default xHTML content
		#
		xhtml_header
		debug_info
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

<h3>`gettext "Panel settings"`</h3>
<form method="get" action="$SCRIPT_NAME">
	<div>
		<input type="submit" value="`gettext "Change Panel password"`" />
		<input type="password" name="panel-pass"/>
	</div>
</form>

EOT
		;;
esac

xhtml_footer
exit 0
