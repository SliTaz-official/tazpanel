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
TEXTDOMAIN='tazpanel'
export TEXTDOMAIN

# Actions commands before page is displayed
case "$QUERY_STRING" in
	start)
		# Here we sleep a bit to let udhcp get the lease before reloading
		# page with status
		/etc/init.d/network.sh start >/dev/null
		sleep 2 ;;
	stop)
		/etc/init.d/network.sh stop >/dev/null ;;
	*)
		continue ;;
esac

#
# Main Commands for pages
#

case "$QUERY_STRING" in
	eth)
		# Wired connections settings
		xhtml_header
		cat << EOT
<h2>`gettext "Ethernet connection`</h2>
<pre>
`grep ^[A-V] /etc/network.conf`
</pre>
EOT
		;;
	wifi)
		# Wireless connections settings
		xhtml_header
		cat << EOT
<h2>`gettext "Wireless connection`</h2>
<pre>
`grep ^WIFI_ /etc/network.conf`
</pre>
EOT
		;;
	*)
		# Main Network page starting with a summary
		xhtml_header
		cat << EOT
<h2>`gettext "Networking`</h2>
<p>
	`gettext "Manage network connection and services`
</p>
<div id="actions">
	<p>
		`gettext "Connection:"`
		<a class="button" href="$SCRIPT_NAME?start">`gettext "Start"`</a>
		<a class="button" href="$SCRIPT_NAME?stop">`gettext "Stop"`</a>
	</p>
</div>

`list_network_interfaces`

<h3>`gettext "Output of ifconfig"`</h3>
<pre>
`ifconfig`
</pre>
EOT
		;;
esac

xhtml_footer
exit 0
