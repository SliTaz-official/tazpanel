#!/bin/sh
#
# Network configuration CGI interface
#

# Common functions from libtazpanel
. lib/libtazpanel
. /etc/network.conf
get_config
header

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel'
export TEXTDOMAIN

TITLE="- Network"

# Catch ESSIDs and format output for GTK tree. We get the list of
# networks by Cell and without spaces.
detect_wifi_networks()
{
	table_start
	cat << EOT
<thead>
	<tr>
		<td>$(gettext "Name")</td>
		<td>$(gettext "Quality")</td>
		<td>$(gettext "Encryption")</td>
		<td>$(gettext "Status")</td>
	</tr>
</thead>
EOT
	if [ -d /sys/class/net/$WIFI_INTERFACE/wireless ]; then
		ifconfig $WIFI_INTERFACE up
		for i in `iwlist $WIFI_INTERFACE scan | sed s/"Cell "/Cell-/ | grep "Cell-" | awk '{print $1}'`
		do
			SCAN=`iwlist $WIFI_INTERFACE scan last | \
				awk '/(Cell|ESS|Qual|Encry|IE: WPA)/ {print}' | \
				sed s/"Cell "/Cell-/ | grep -A 5 "$i"`
			ESSID=`echo $SCAN | cut -d '"' -f 2`
			if echo "$SCAN" | grep -q Quality; then
				QUALITY=`echo $SCAN | sed 's/.*Quality=\([^ ]*\).*/\1/' | sed 's/.*Quality:\([^ ]*\).*/\1/'`
			else
				QUALITY="-"
			fi
			ENCRYPTION=`echo $SCAN | sed 's/.*key:\([^ ]*\).*/\1/'`
			# Check encryption type
			if echo "$SCAN" | grep -q WPA; then
				ENCRYPTION="${ENCRYPTION} (WPA)"
			fi
			# Connected or not connected...
			if ifconfig | grep -A 1 $WIFI_INTERFACE | \
				grep -q inet && iwconfig $WIFI_INTERFACE | \
				grep ESSID | grep -q -w "$ESSID"; then
				STATUS=$(gettext "Connected")
			else
				STATUS="-"
			fi
			echo '<tr>'
			echo "<td><img src='$IMAGES/wireless.png' />$ESSID</td>"
			echo "<td>$QUALITY</td><td>$ENCRYPTION</td><td>$STATUS</td>"
			echo '</tr>'
		done
	fi
	table_end
}

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
		if [ "$(GET ip)" ]; then
			LOADING_MSG=$(gettext "Setting up static IP...")
			loading_msg
			sed -i \
				-e s"/^INTERFACE=.*/INTERFACE=\"$(GET iface)\""/ \
				-e s'/^DHCP=.*/DHCP="no"/' \
				-e s'/^WIFI=.*/WIFI="no"/' \
				-e s'/^STATIC=.*/STATIC="yes"/' \
				-e s"/^NETMASK=.*/NETMASK=\"$(GET netmask)\"/" \
				-e s"/^GATEWAY=.*/GATEWAY=\"$(GET gateway)\"/" \
				-e s"/^DNS_SERVER=.*/DNS_SERVER=\"$(GET dns)\"/" \
				-e s"/^IP=.*/IP=\"$(GET ip)\"/" /etc/network.conf
			/etc/init.d/network stop | log
			sleep 2
			/etc/init.d/network start | log
		fi
		. /etc/network.conf
		cat << EOT
<h2>`gettext "Ethernet connection`</h2>

<h3>$(gettext "Setup a static IP")</h3>
<form method="get" action="$SCRIPT_NAME">
	<input type="hidden" name="eth" />
	$(table_start)
	<thead>
		<tr>
			<td>$(gettext "Name")</td>
			<td>$(gettext "Value")</td>
		</tr>
	</thead>
	<tr>
		<td>$(gettext "Interface")</td>
		<td><input type="text" name="iface" size="20" value="$INTERFACE" /></td>
	</tr>
	<tr>
		<td>$(gettext "IP address")</td>
		<td><input type="text" name="ip" size="20" value="$IP" /></td>
	</tr>
	<tr>
		<td>$(gettext "Netmask")</td>
		<td><input type="text" name="netmask" size="20" value="$NETMASK" /></td>
	</tr>
	<tr>
		<td>$(gettext "Gateway")</td>
		<td><input type="text" name="gateway" size="20" value="$GATEWAY" /></td>
	</tr>
	<tr>
		<td>$(gettext "DNS server")</td>
		<td><input type="text" name="dns" size="20" value="$DNS_SERVER" /></td>
	</tr>
	$(table_end)
		<input type="submit" value="`gettext "Activate"`">
</form>

<h3>$(gettext "Configuration file")</h3>
<p>
$(gettext "These values are the ethernet settings in the main
/etc/network.conf configuration file")
</p>
<pre>
$(grep ^[A-V] /etc/network.conf | syntax_highlighter conf)
</pre>
<a class="button" href="index.cgi?file=/etc/network.conf&action=edit">
	<img src="$IMAGES/edit.png" />$(gettext "Manual Edit")</a>
EOT
		;;
	*\ wifi\ *)
		# Wireless connections settings
		xhtml_header
		LOADING_MSG=$(gettext "Scanning wireless interface...")
		loading_msg
		cat << EOT
<h2>`gettext "Wireless connection`</h2>
<div id="actions">
	<a class="button" href="$SCRIPT_NAME?wifi=scan">
		<img src="$IMAGES/recharge.png" />$(gettext "Scan")</a>
</div>
$(detect_wifi_networks)
EOT
	cat << EOT
<h3>$(gettext "Configuration file")</h3>
<p>
$(gettext "These values are the wifi settings in the main
/etc/network.conf configuration file")
</p>
<pre>
$(grep ^WIFI /etc/network.conf | syntax_highlighter conf)
</pre>
<a class="button" href="index.cgi?file=/etc/network.conf&action=edit">
	<img src="$IMAGES/edit.png" />$(gettext "Manual Edit")</a>

<h3>$(gettext "Output of") iwconfig</h3>
<pre>
$(iwconfig)
</pre>
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

$(list_network_interfaces)

<h3>$(gettext "Output of ") ifconfig</h3>
<pre>
$(ifconfig)
</pre>

<h3>`gettext "Routing table"`</h3>
<pre>
$(route -n)
</pre>

<h3>`gettext "Domain name resolution"`</h3>
<pre>
$(cat /etc/resolv.conf)
</pre>

<h3>`gettext "ARP table"`</h3>
<pre>
$(arp)
</pre>
EOT
		;;
esac

xhtml_footer
exit 0
