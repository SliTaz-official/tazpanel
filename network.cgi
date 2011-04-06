#!/bin/sh
#
# Network configuration CGI interface
#
echo "Content-Type: text/html"
echo ""

# Common functions from libtazpanel
. lib/libtazpanel
get_config

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel-cgi'
export TEXTDOMAIN

#
# Commands
#

case "$QUERY_STRING" in
	*)
		#
		# Network configuration
		#
		TITLE="- Network"
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Networking`</h2>
	<p>`gettext "Manage network connection and services`</p>
</div>

`list_network_interfaces`

<h3>Output of: ifconfig -a</h3>
<pre>
`ifconfig -a`
</pre>
EOT
		;;
esac

xhtml_footer
exit 0
