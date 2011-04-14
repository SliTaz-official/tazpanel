#!/bin/sh
#
# Network configuration CGI interface
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

TITLE="- Network"

# Actions commands before page is displayed
case " $(GET) " in
	*\ start\ *)
		# Here we sleep a bit to let udhcp get the lease before reloading
		# page with status
		/etc/init.d/network.sh start | log
		sleep 2 ;;
	*\ stop\ *)
		/etc/init.d/network.sh stop | log ;;
	*)
		continue ;;
esac

#
# Main Commands for pages
#

case " $(GET) " in
	*\ eth\ *)
		# Wired connections settings
		xhtml_header
		
		cat << EOT
<h2>`gettext "Ethernet connection`</h2>
<pre>
`grep ^[A-V] /etc/network.conf`
</pre>
EOT
		;;
	*\ wifi\ *)
		# Wireless connections settings
		xhtml_header
		cat << EOT
<h2>`gettext "Wireless connection`</h2>

<h3>$(gettext "Configuration file")</h3>
<p>
$(gettext "These values are the wifi settings in the main
/etc/network.conf configuration file")
</p>
<pre>
$(grep ^WIFI_ /etc/network.conf | syntax_highlighter conf)
</pre>
<a class="button" href="index.cgi?file=/etc/network.conf&action=edit">
	<img src="$IMAGES/edit.png" />$(gettext "Manual Edit")</a>
EOT
		;;
	*)
		# Main Network page starting with a summary
		xhtml_header
		
		cat << EOT
<h2>`gettext "Networking`</h2>
<p>
	`gettext "Manage network connections and services`
</p>
<div id="actions">
	<div class="float-left">
		`gettext "Connection:"`
		<a class="button" href="$SCRIPT_NAME?start">`gettext "Start"`</a>
		<a class="button" href="$SCRIPT_NAME?stop">`gettext "Stop"`</a>
	</div>
	<div class="float-right">
		`gettext "Configuration file:"`
		<a class="button" href="index.cgi?file=/etc/network.conf">network.conf</a>
	</div>
</div>

`list_network_interfaces`

<h3>`gettext "Output of ifconfig"`</h3>
<pre>
`ifconfig`
</pre>

<h3>`gettext "Routing table"`</h3>
<pre>
`route -n`
</pre>

<h3>`gettext "Domain name resolution"`</h3>
<pre>
`cat /etc/resolv.conf`
</pre>

<h3>`gettext "ARP table"`</h3>
<pre>
`arp`
</pre>
EOT
		;;
esac

xhtml_footer
exit 0
