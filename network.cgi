#!/bin/sh
#
# Network configuration CGI interface
#
# Copyright (C) 2012 SliTaz GNU/Linux - BSD License
#

# Common functions from libtazpanel
. lib/libtazpanel
get_config
header

TITLE=$(gettext 'TazPanel - Network')

# Catch ESSIDs and format output for GTK tree. We get the list of
# networks by Cell and without spaces.
detect_wifi_networks()
{
	cat << EOT
<table class="zebra outbox">
	<thead>
		<tr>
			<td>$(gettext 'Name')</td>
			<td>$(gettext 'Quality')</td>
			<td>$(gettext 'Encryption')</td>
			<td>$(gettext 'Status')</td>
		</tr>
	</thead>
	<tbody>
EOT
	if [ -d /sys/class/net/$WIFI_INTERFACE/wireless ]; then
		ifconfig $WIFI_INTERFACE up
		for i in $(iwlist $WIFI_INTERFACE scan | sed '/Cell /!d;s/.*Cell \([^ ]*\).*/Cell.\1/')
		do
			SCAN=$(iwlist $WIFI_INTERFACE scan last | sed "/$i/,/Cell/!d" | sed '$d')
			ESSID=$(echo $SCAN | sed 's/.*ESSID:"\([^"]*\).*/\1/')
			if echo "$SCAN" | grep -q Quality; then
				QUALITY=$(echo $SCAN | sed 's/.*Quality:\([^ ]*\).*/\1/')
			else
				QUALITY="-"
			fi
			ENCRYPTION=$(echo $SCAN | sed 's/.*key:\([^ ]*\).*/\1/')
			# Check encryption type
			if echo "$SCAN" | grep -q WPA*; then
				ENCRYPTION="WPA"
			fi
			if echo $SCAN | grep -q 'Mode:Managed'; then
				AP="&ap=$(echo $SCAN | sed 's/.*Address: \([^ ]*\).*/\1/')"
			else
				AP=""
			fi
			# Connected or not connected...
			if ifconfig | grep -A 1 $WIFI_INTERFACE | \
				fgrep -q inet && iwconfig $WIFI_INTERFACE | \
				fgrep -q "ESSID:\"$ESSID\""; then
				status=$(gettext 'Connected')
			else
				status="---"
			fi
			echo '<tr>'
			echo "<td><a href=\"$SCRIPT_NAME?wifi&select=$ESSID&keytype=$ENCRYPTION&$AP\">
				<img src='$IMAGES/wireless.png' />$ESSID</a></td>"
			echo "<td>$QUALITY</td><td>$ENCRYPTION</td><td>$status $ip</td>"
			echo '</tr>'
		done
	fi
	cat << EOT
	</tbody>
</table>
EOT
}

# Start a wifi connection
start_wifi() {
	sed -i \
		-e s'/^DHCP=.*/DHCP="yes"/' \
		-e s'/^WIFI=.*/WIFI="yes"/' \
		-e s'/^STATIC=.*/STATIC="no"/' /etc/network.conf
	ifconfig $WIFI_INTERFACE up
	iwconfig $WIFI_INTERFACE txpower auto
	/etc/init.d/network.sh restart | log
	sleep 2
}

# Actions commands before page is displayed
case " $(GET) " in
	*\ start\ *)
		# Here we sleep a bit to let udhcp get the lease before reloading
		# the page with status
		/etc/init.d/network.sh start | log
		sleep 2 ;;
	*\ stop\ *)
		/etc/init.d/network.sh stop | log ;;
	*\ restart\ *)
		/etc/init.d/network.sh restart | log ;;
	*\ start-wifi\ *) start_wifi ;;
	*\ hostname\ *)
		get_hostname="$(GET hostname)"
		echo $(eval_gettext 'Changed hostname: $get_hostname') | log
		echo "$get_hostname" > /etc/hostname ;;
esac

# Get values only now since they could have been modified by actions.
. /etc/network.conf

#
# Main Commands for pages
#

case " $(GET) " in
	*\ scan\ *)
		# Scan open ports
		scan=$(GET scan)
		xhtml_header
		LOADING_MSG=$(gettext 'Scanning open ports...')
		loading_msg
		cat << EOT
<h2>$(eval_gettext 'Port scanning for $scan')</h2>

<pre>$(pscan -b $scan)</pre>
EOT
		;;

	*\ eth\ *)
		# Wired connections settings
		xhtml_header
		if [ "$(GET ip)" ]; then
			DHCP=no
			STATIC=no
			[ -n "$(GET dhcp)" ] && DHCP=yes
			[ -n "$(GET static)" ] && STATIC=yes
			LOADING_MSG=$(gettext 'Setting up IP...')
			loading_msg
			sed -i \
				-e s"/^INTERFACE=.*/INTERFACE=\"$(GET iface)\""/ \
				-e s"/^DHCP=.*/DHCP=\"$DHCP\"/" \
				-e s"/^STATIC=.*/STATIC=\"$STATIC\"/" \
				-e s"/^NETMASK=.*/NETMASK=\"$(GET netmask)\"/" \
				-e s"/^GATEWAY=.*/GATEWAY=\"$(GET gateway)\"/" \
				-e s"/^DNS_SERVER=.*/DNS_SERVER=\"$(GET dns)\"/" \
				-e s"/^IP=.*/IP=\"$(GET ip)\"/" /etc/network.conf
			/etc/init.d/network stop | log
			sleep 2
			/etc/init.d/network start | log
			. /etc/network.conf
		fi
		cat << EOT
<h2>$(gettext 'Ethernet connection')</h2>

<p>$(gettext "Here you can configure a wired connection using DHCP to \
automatically get a random IP or configure a static/fixed IP")</p>

<section>
<h3>$(gettext 'Configuration')</h3>
<form method="get" action="$SCRIPT_NAME">
	<input type="hidden" name="eth" />
	<table>
	<thead>
		<tr>
			<td>$(gettext 'Name')</td>
			<td>$(gettext 'Value')</td>
		</tr>
	</thead>
	<tbody>
	<tr>
		<td>$(gettext 'Interface')</td>
		<td><input type="text" name="iface" size="20" value="$INTERFACE" /></td>
	</tr>
	<tr>
		<td>$(gettext 'IP address')</td>
		<td><input type="text" name="ip" size="20" value="$IP" /></td>
	</tr>
	<tr>
		<td>$(gettext 'Netmask')</td>
		<td><input type="text" name="netmask" size="20" value="$NETMASK" /></td>
	</tr>
	<tr>
		<td>$(gettext 'Gateway')</td>
		<td><input type="text" name="gateway" size="20" value="$GATEWAY" /></td>
	</tr>
	<tr>
		<td>$(gettext 'DNS server')</td>
		<td><input type="text" name="dns" size="20" value="$DNS_SERVER" /></td>
	</tr>
	</tbody>
	</table>
		<input type="submit" name="static" value="$(gettext 'Activate (static)')">
		<input type="submit" name="dhcp" value="$(gettext 'Activate (DHCP)')">
		<input type="submit" name="disable" value="$(gettext 'Disable')">
</form>
</section>

<section>
<h3>$(gettext 'Configuration file')</h3>

<p>$(gettext "These values are the ethernet settings in the main \
/etc/network.conf configuration file")</p>
<pre>
$(grep ^[A-V] /etc/network.conf | syntax_highlighter conf)
</pre>
<a class="button" href="index.cgi?file=/etc/network.conf&action=edit">
	<img src="$IMAGES/edit.png" />$(gettext 'Manual Edit')</a>
</section>
EOT
		;;
	*\ wifi\ *)
		# Wireless connections settings
		xhtml_header
		LOADING_MSG=$(gettext 'Scanning wireless interface...')
		loading_msg
		. /etc/network.conf
		cat << EOT
<h2>$(gettext 'Wireless connection')</h2>
<div id="actions">
	<a class="button" href="$SCRIPT_NAME?wifi&start-wifi=start-wifi">
		<img src="$IMAGES/start.png" />$(gettext 'Start')</a>
	<a class="button" href="$SCRIPT_NAME?wifi&stop=stop">
		<img src="$IMAGES/stop.png" />$(gettext 'Stop')</a>
	<a class="button" href="$SCRIPT_NAME?wifi=scan">
		<img src="$IMAGES/recharge.png" />$(gettext 'Scan')</a>
</div>
$(detect_wifi_networks)
EOT
		WIFI_AP="$(GET ap)"
		WIFI_KEY="$(GET key)"
		case "$(GET keytype)" in
		''|off)	WIFI_KEY_TYPE=none ;;
		*)	WIFI_KEY_TYPE=any  ;;
		esac
		if [ "$(GET essid)" ]; then
			/etc/init.d/network.sh stop | log
			sed -i \
				-e s"/^WIFI_ESSID=.*/WIFI_ESSID=\"$(GET essid)\""/ \
				-e s"/^WIFI_KEY=.*/WIFI_KEY=\"$WIFI_KEY\"/" \
				-e s"/^WIFI_KEY_TYPE=.*/WIFI_KEY_TYPE=\"$WIFI_KEY_TYPE\"/" \
				-e s"/^WIFI_AP=.*/WIFI_AP=\"$WIFI_AP\"/" \
				/etc/network.conf
			. /etc/network.conf
			start_wifi
		fi
		# ESSID names are clickable
		if [ "$(GET select)" ]; then
			if [ "$(GET select)" != "$WIFI_ESSID" ]; then
				WIFI_KEY=""
			fi
			WIFI_ESSID="$(GET select)"
		fi
	cat << EOT
<section>
<h3>$(gettext 'Connection')</h3>
<form method="get" action="$SCRIPT_NAME">
	<input type="hidden" name="connect-wifi" />
	$(table_start)
	<thead>
		<tr>
			<td>$(gettext 'Name')</td>
			<td>$(gettext 'Value')</td>
		</tr>
	</thead>
	<tr>
		<td>$(gettext 'Wifi name (ESSID)')</td>
		<td><input type="text" name="essid" size="30" value="$WIFI_ESSID" /></td>
	</tr>
	<tr>
		<td>$(gettext 'Password (Wifi key)')</td>
		<td><input type="password" name="key" size="30" value="$WIFI_KEY" /></td>
	</tr>
	<tr>
		<td>$(gettext 'Encryption type')</td>
		<td><input type="text" name="keytype" size="30" value="$WIFI_KEY_TYPE" /></td>
	</tr>
	<tr>
		<td>$(gettext 'Access point')</td>
		<td><input type="text" name="ap" size="30" value="$WIFI_AP" /></td>
	</tr>
	$(table_end)
		<input type="submit" name="wifi" value="$(gettext 'Configure')" />
</form>
</section>

<section>
<h3>$(gettext 'Configuration file')</h3>

<p>$(gettext "These values are the wifi settings in the main /etc/network.conf \
configuration file")</p>

<pre>$(grep ^WIFI /etc/network.conf | syntax_highlighter conf)</pre>

<a class="button" href="index.cgi?file=/etc/network.conf&action=edit">
	<img src="$IMAGES/edit.png" />$(gettext 'Manual Edit')</a>
</section>

<section>
<h3>$(gettext 'Output of iwconfig')</h3>

<pre>$(iwconfig)</pre>
</section>
EOT
		;;
	*)
		# Main Network page starting with a summary
		xhtml_header
		hostname=$(cat /etc/hostname)
		cat << EOT
<h2>$(gettext 'Networking')</h2>

<p>$(gettext 'Manage network connections and services')</p>

<section>
<div id="actions">
	<div class="float-left">
		<a class="button" href="$SCRIPT_NAME?start">
			<img src="$IMAGES/start.png" />$(gettext 'Start')</a>
		<a class="button" href="$SCRIPT_NAME?stop">
			<img src="$IMAGES/stop.png" />$(gettext 'Stop')</a>
		<a class="button" href="$SCRIPT_NAME?restart">
			<img src="$IMAGES/recharge.png" />$(gettext 'Restart')</a>
	</div>
	<div class="float-right">
		$(gettext 'Configuration:')
		<a class="button" href="index.cgi?file=/etc/network.conf">network.conf</a>
		<a class="button" href="$SCRIPT_NAME?eth">Ethernet</a>
		<a class="button" href="$SCRIPT_NAME?wifi">Wireless</a>
	</div>
</div>

$(list_network_interfaces)
</section>

<section>
<h3 id="hosts">$(gettext 'Hosts')</h3>

<pre>$(cat /etc/hosts)</pre>

<a class="button" href="index.cgi?file=/etc/hosts&action=edit">
	<img src="$IMAGES/edit.png" />$(gettext 'Edit hosts')</a>
</section>

<section>
<h3>$(gettext 'Hostname')</h3>

<form method="get" name="$SCRIPT_NAME">
	<input type="text" name="hostname" value="$hostname" />
	<input type="submit" value="$(gettext 'Change hostname')" />
</form>
</section>

<section>
<h3 id="ifconfig">$(gettext 'Output of ifconfig')</h3>

<pre>$(ifconfig)</pre>
</section>

<section>
<h3 id="routing">$(gettext 'Routing table')</h3>

<pre>$(route -n)</pre>
</section>

<section>
<h3 id="dns">$(gettext 'Domain name resolution')</h3>

<pre>$(cat /etc/resolv.conf)</pre>
</section>

<section>
<h3 id="arp">$(gettext 'ARP table')</h3>

<pre>$(arp)</pre>
</section>

<section>
<h3 id="connections">$(gettext 'IP Connections')</h3>

<pre>
$(netstat -anp 2> /dev/null | sed -e '/UNIX domain sockets/,$d' \
-e 's#\([0-9]*\)/#<a href="boot.cgi?daemons=pid=\1">\1</a>/#')
</pre>
</section>
EOT
		;;
esac

xhtml_footer
exit 0
