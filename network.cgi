#!/bin/sh
#
# Network configuration CGI interface
#
# Copyright (C) 2012-2015 SliTaz GNU/Linux - BSD License
#


# Common functions from libtazpanel

. lib/libtazpanel
get_config
header

TITLE=$(gettext 'TazPanel - Network')


# Start a Wi-Fi connection

start_wifi() {
	sed -i \
		-e 's|^WIFI=.*|WIFI="yes"|' \
		-e 's|^DHCP=.*|DHCP="yes"|' \
		-e 's|^STATIC=.*|STATIC="no"|' /etc/network.conf
	ifconfig $WIFI_INTERFACE up
	iwconfig $WIFI_INTERFACE txpower auto
	/etc/init.d/network.sh restart | log
	# Sleep until connection established (max 20 seconds)
	for i in $(seq 20); do
		[ -n "$(iwconfig 2>/dev/null | fgrep Link)" ] && break
		sleep 1
	done
}


# Use /etc/wpa/wpa.conf as single database for known networks, passwords, etc.
# Translate this data to use in javascript.

parse_wpa_conf() {
	awk '
	BEGIN { print "networks = ["; begin_list = 1; network = 0; }
	{
		if ($0 == "network={") {
			if (begin_list == 0) print ",";
			begin_list = 0;
			printf "{"; begin_obj = 1;
			network = 1; next;
		}
		if (network == 1) {
			if ($0 ~ "=") {
				if (begin_obj == 0) printf ", ";
				begin_obj = 0;
				split($0, a, "=");
				if (a[2] ~ "\"")
					printf "%s:%s", a[1], a[2];
				else
					printf "%s:\"%s\"", a[1], a[2];
			}
		}
		if (network == 1 && $0 ~ "}") { printf "}"; network = 0; next; }
	}
	END {print "\n];"}
	' /etc/wpa/wpa.conf | sed 's|\t||g;'
}


# Waiting for network link up

wait_up() {
	for i in $(seq 10); do
		[ -z "$(cat /sys/class/net/*/operstate | fgrep up)"] && sleep 1
	done
}

# Actions commands before page is displayed

case " $(GET) " in
	*\ start\ *)
		/etc/init.d/network.sh start | log
		# Here we sleep a bit to let udhcp get the lease before reloading
		# the page with status
		wait_up ;;
	*\ stop\ *)
		/etc/init.d/network.sh stop | log ;;
	*\ restart\ *)
		/etc/init.d/network.sh restart | log
		wait_up ;;
	*\ start-wifi\ *)
		start_wifi ;;
	*\ host\ *)
		get_hostname="$(GET host)"
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
		scan=$(GET scan); back=$(GET back)
		xhtml_header
		LOADING_MSG=$(gettext 'Scanning open ports...'); loading_msg

		cat <<EOT
<section>
	<header>
		$(eval_gettext 'Port scanning for $scan')
		$(back_button "$back" "$(gettext 'Network')" "")
	</header>
	<pre>$(pscan -b $scan)</pre>
</section>
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
			LOADING_MSG=$(gettext 'Setting up IP...'); loading_msg

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

		PAR1="size=\"20\" required"; PAR="$PAR1 pattern=\"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\" data-x=\"Four numbers, each in range 0-255, delimited by full stop.\""
		cat <<EOT
<h2>$(gettext 'Ethernet connection')</h2>

<p>$(gettext "Here you can configure a wired connection using DHCP to \
automatically get a random IP or configure a static/fixed IP")</p>

<section>
	<header>$(gettext 'Configuration')</header>
	<form id="conf">
		<input type="hidden" name="eth"/>
		<div>
			<table>
				<tr><td>$(gettext 'Interface')</td>
					<td><select name="iface" value="$INTERFACE" style="width:100%"/>
					$(cd /sys/class/net; ls -1 | awk -viface="$INTERFACE" '{
						sel = ($0 == iface) ? " selected":""
						printf "<option value=\"%s\"%s>%s", $0, sel, $0
					}')
					</select></td>
				</tr>
				<tr><td>&nbsp;</td>
					<td><label><input type="checkbox" name="staticip" id="staticip"/>
						$(gettext 'Use static IP')</td>
				<tr><td>$(gettext 'IP address')</td>
					<td><input type="text" name="ip"      id="st1" value="$IP"         $PAR/></td>
				</tr>
				<tr><td>$(gettext 'Netmask')</td>
					<td><input type="text" name="netmask" id="st2" value="$NETMASK"    $PAR/></td>
				</tr>
				<tr><td>$(gettext 'Gateway')</td>
					<td><input type="text" name="gateway" id="st3" value="$GATEWAY"    $PAR/></td>
				</tr>
				<tr><td>$(gettext 'DNS server')</td>
					<td><input type="text" name="dns"     id="st4" value="$DNS_SERVER" $PAR/></td>
				</tr>
			</table>
		</div>
	</form>
	<footer><!--
		--><button form="conf" type="submit" name="static"  data-icon="ok"    >$(gettext 'Activate (static)')</button><!--
		--><button form="conf" type="submit" name="dhcp"    data-icon="ok"    >$(gettext 'Activate (DHCP)'  )</button><!--
		--><button form="conf" name="disable" data-icon="cancel">$(gettext 'Disable'          )</button><!--
	--></footer>
</section>

<script type="text/javascript">
	document.getElementById('staticip').onchange = static_change;

	function static_change() {
		staticip = document.getElementById('staticip');
		alert(staticip.checked);
	}
</script>

<section>
	<header>
		$(gettext 'Configuration file')
		<form action="index.cgi">
			<input type="hidden" name="file" value="/etc/network.conf"/>
			<button name="action" value="edit" data-icon="edit">$(gettext 'Edit')</button>
		</form>
	</header>
	<div>$(gettext "These values are the ethernet settings in the main /etc/network.conf configuration file")</div>
	<pre>$(awk '{if($1 !~ "WIFI" && $1 !~ "#" && $1 != ""){print $0}}' /etc/network.conf | syntax_highlighter conf)</pre>
</section>
EOT
		;;



	*\ wifi_list\ *)
		# Catch ESSIDs and format output.
		# We get the list of networks by Cell and without spaces.

		HIDDEN="$(gettext '(hidden)')"

		cat <<EOT
<table class="wide center zebra">
	<thead>
		<tr>
			<td>$(gettext 'Name')</td>
			<td>$(gettext 'Signal level')</td>
			<td>$(gettext 'Channel')</td>
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

				BSSID=$(echo "$SCAN" | sed -n 's|.*Address: \([^ ]*\).*|\1|p')

				CHANNEL=$(echo "$SCAN" | sed -n 's|.*Channel[:=]\([^ ]*\).*|\1|p')

				QUALITY=$(echo "$SCAN" | sed -n 's|.*Quality[:=]\([^ ]*\).*|\1|p')
				QUALITY_ICON="lvl$(( 5*${QUALITY:-0} ))"		# lvl0 .. lvl4, lvl5
				LEVEL=$(echo "$SCAN" | sed -n 's|.*Signal level[:=]\([^ ]*\).*|\1|p; s|-|−|')

				ENCRYPTION=$(echo "$SCAN" | sed -n 's|.*Encryption key[:=]\([^ ]*\).*|\1|p')		# on/off

				ESSID=$(echo "$SCAN" | sed -n 's|.*ESSID:"\([^"]*\).*|\1|p')

				# WPA Type - Group Cipher - Pairwise Ciphers - Authentication Suites
				# {WPA|WPA2}-{TKIP|CCMP}-{TKIP|CCMP|TKIP CCMP}-{PSK|802.1x}
				#CAPABILITIES="$(echo "$SCAN" | grep -e 'IE: .*WPA*' -A3 | cut -d: -f2 | sed -e 's|^ ||' -e '/WPA2/s|.*|=WPA2|' -e '/WPA /s|.*|=WPA|' -e '/--/d' | tr '\n' '-' | tr '=' '\n' | sed -e '/^$/d' -e 's|-$||')"

				# Authentication type
				AUTH="$(echo "$SCAN" | sed -n 's|.*Authentication Suites[^:]*: *\(.*\)|\1|p')"
				if [ -n "$(echo -n $AUTH | fgrep PSK)" ]; then
					# WPA-Personal. Authentication using password (PSK = pre-shared key)
					WIFI_KEY_TYPE='WPA'
				elif [ -n "$(echo -n $AUTH | fgrep 802.1x)" ]; then
					# WPA-Enterprise. Authentication using username, password, certificates...
					WIFI_KEY_TYPE='EAP'
				else
					WIFI_KEY_TYPE='NONE'
				fi

				# Check encryption type
				if [ "$ENCRYPTION" == 'on' ]; then
					# "WPA" or "WPA2" or "WPA/WPA2" (maybe also "WPA2/WPA")
					ENC_SIMPLE=$(echo "$SCAN" | sed -n '/.*WPA.*/ s|.*\(WPA[^ ]*\).*|\1|p')
					ENC_SIMPLE=$(echo $ENC_SIMPLE | sed 's| |/|')
					ENC_ICON='sechi' # high
					if [ -z "$ENC_SIMPLE" ]; then
						WIFI_KEY_TYPE='WEP'
						ENC_SIMPLE='WEP'; ENC_ICON='secmi' # middle
					fi
				else
					WIFI_KEY_TYPE='NONE'
					ENC_SIMPLE="$(gettext 'None')"; ENC_ICON='seclo' # low
				fi

				# 
				#if echo $SCAN | grep -q 'Mode:Managed'; then
				#	AP="&amp;ap=$(echo $SCAN | sed 's/.*Address: \([^ ]*\).*/\1/')"
				#else
				#	AP=''
				#fi

				# Connected or not connected...
				if  ifconfig $WIFI_INTERFACE | fgrep -q inet && \
					iwconfig $WIFI_INTERFACE | fgrep -q "ESSID:\"$ESSID\""; then
					status="$(gettext 'Connected')"
				else
					status='---'
				fi

				cat <<EOT
<tr>
	<td><a data-icon="wifi" onclick="loadcfg('$ESSID', '$BSSID', '$WIFI_KEY_TYPE')">${ESSID:-$HIDDEN}</a></td>
	<td><span data-icon="$QUALITY_ICON" title="Quality: $QUALITY"> $LEVEL dBm</span></td>
	<td>$CHANNEL</td>
	<td><span data-icon="$ENC_ICON">$ENC_SIMPLE</span></td>
	<td>$status</td>
</tr>
EOT
			done
		fi
		cat <<EOT
	</tbody>
</table>
EOT
		exit 0
		;;


	*\ wifi\ *)
		# Wireless connections settings
		xhtml_header

		. /etc/network.conf
		cat <<EOT
<h2>$(gettext 'Wireless connection')</h2>

<form>
	<input type="hidden" name="wifi"/>
EOT

		start_disabled=''; stop_disabled=''
		if iwconfig 2>/dev/null | grep -q 'Tx-Power=off'; then
			stop_disabled='disabled'
		else
			start_disabled='disabled'
		fi

		cat <<EOT
	   <button name="start-wifi" data-icon="start"   $start_disabled>$(gettext 'Start')</button><!--
	--><button name="stop"       data-icon="stop"    $stop_disabled >$(gettext 'Stop' )</button><!--
	--><button type="submit"     data-icon="refresh" $stop_disabled >$(gettext 'Scan' )</button>
</form>
EOT

		if [ -n "$start_disabled" ]; then
			cat <<EOT
<section id="wifiList">
	<div style="text-align: center;"><span id="ajaxStatus"></span>$(gettext 'Scanning wireless interface...')</div>
</section>

<script type="text/javascript">
	ajax('/network.cgi?wifi_list', '1', 'wifiList');
	$(parse_wpa_conf)
</script>
EOT

			ESSID="$(GET essid)"
			#WIFI_KEY_TYPE="$(GET keyType)"
			#WIFI_KEY="$(GET key)"
			#WIFI_AP="$(GET ap)"

			if [ -n "$ESSID" ]; then
				/etc/init.d/network.sh stop | log
				sed -i \
					-e "s/^WIFI_ESSID=.*/WIFI_ESSID=\"$essid\"/" \
					-e "s/^WIFI_KEY_TYPE=.*/WIFI_KEY_TYPE=\"$WIFI_KEY_TYPE\"/" \
					-e "s/^WIFI_KEY=.*/WIFI_KEY=\"$WIFI_KEY\"/" \
					-e "s/^WIFI_AP=.*/WIFI_AP=\"$WIFI_AP\"/" \
					/etc/network.conf
				. /etc/network.conf
				start_wifi
			fi

			# ESSID names are clickable
			#SELECT="$(GET select)"
			#if [ -n "$SELECT" ]; then
			#	[ "$SELECT" != "$WIFI_ESSID" ] && WIFI_KEY=''
			#	WIFI_ESSID="$SELECT"
			#fi

			cat <<EOT
<section>
	<header>$(gettext 'Connection')</header>
	<div>
		<form id="connection">
			<input type="hidden" name="connect-wifi"/>
			<table>
				<tr><td>$(gettext 'Network SSID')</td>
					<td><input type="text" name="essid" value="$WIFI_ESSID" id="essid"/></td>
				</tr>

				<tr><td>$(gettext 'Security')</td>
					<td><select name="keyType" id="keyType">
							<option value="NONE">$(gettext 'None')</option>
							<option value="WEP" >WEP</option>
							<option value="WPA" >WPA/WPA2 PSK</option>
							<option value="EAP" >802.1x EAP</option>
						</select>
					</td>
				</tr>

				<tr class="eap">
					<td><div>$(gettext 'EAP method')</div></td>
					<td><div><select name="eap" id="eap">
							<option value="PEAP">PEAP</option>
							<option value="TLS" >TLS</option>
							<option value="TTLS">TTLS</option>
							<option value="PWD" >PWD</option>
						</select>
					</div></td>
				</tr>

				<tr class="eap1">
					<td><div>$(gettext 'Phase 2 authentication')</div></td>
					<td><div><select name="phase2" id="phase2">
							<option value="none"    >$(gettext 'None')</option>
							<option value="pap"     >PAP</option>
							<option value="mschap"  >MSCHAP</option>
							<option value="mschapv2">MSCHAPV2</option>
							<option value="gtc"     >GTC</option>
						</select>
					</div></td>
				</tr>

				<tr class="eap1">
					<td><div>$(gettext 'CA certificate')</div></td>
					<td><div><input type="text" name="caCert" id="caCert"></div></td>
				</tr>

				<tr class="eap1">
					<td><div>$(gettext 'User certificate')</div></td>
					<td><div><input type="text" name="clientCert" id="clientCert"></div></td>
				</tr>

				<tr class="eap">
					<td><div>$(gettext 'Identity')</div></td>
					<td><div><input type="text" name="identity" id="identity"></div></td>
				</tr>

				<tr class="eap1">
					<td><div>$(gettext 'Anonymous identity')</div></td>
					<td><div><input type="text" name="anonymousIdentity" id="anonymousIdentity"></div></td>
				</tr>

				<tr class="wep wpa eap">
					<td><div>$(gettext 'Password')</div></td>
					<td><div>
						<input type="password" name="password" value="$WIFI_KEY" id="password"/>
						<span data-img="view" title="$(gettext 'Show password')"
							onmousedown="document.getElementById('password').type='text'; return false"
							  onmouseup="document.getElementById('password').type='password'"
							 onmouseout="document.getElementById('password').type='password'"
						></span>
					</div></td>
				</tr>


<!--
				<tr><td>$(gettext 'Access point')</td>
					<td><input type="text" name="ap" value="$WIFI_AP"/></td>
				</tr>
-->

				<script type="text/javascript">
function wifiSettingsChange() {
	document.getElementById('connection').className = 
		document.getElementById('keyType').value.toLowerCase() + ' ' + 
		document.getElementById('eap').value.toLowerCase();
}
document.getElementById('keyType').onchange = wifiSettingsChange;
document.getElementById('eap').onchange = wifiSettingsChange;

document.getElementById('keyType').value = "$WIFI_KEY_TYPE"; wifiSettingsChange();
				</script>

				<style type="text/css">
#connection input[type="text"], #connection input[type="password"] { width: 14rem; }
#connection select { width: 14.4rem; }

#connection td { padding: 0; margin: 0; }
#connection [class] div {
	max-height: 0; overflow: hidden; padding: 0; margin: 0;
	-webkit-transition: all 0.5s ease-in-out;
	   -moz-transition: all 0.5s ease-in-out;
	        transition: all 0.5s ease-in-out;
}
.wep .wep div, .wpa .wpa div, .eap .eap div,
.eap.peap .eap1 div, .eap.tls .eap1 div, .eap.ttls .eap1 div {
	max-height: 2em !important;
}
				</style>

			</table>
		</form>
	</div>
	<footer>
		<button form="connection" type="submit" name="wifi" data-icon="ok">$(gettext 'Configure')</button>
	</footer>
</section>
EOT
		fi

		cat <<EOT
<section>
	<header>
		$(gettext 'Configuration file')
		<form action="index.cgi">
			<input type="hidden" name="file" value="/etc/network.conf"/>
			<button name="action" value="edit" data-icon="edit">$(gettext 'Edit')</button>
		</form>
	</header>
	<div>$(gettext "These values are the wifi settings in the main /etc/network.conf configuration file")</div>
	<pre>$(grep ^WIFI /etc/network.conf | sed '/WIFI_KEY=/s|".*"|"********"|' | syntax_highlighter conf)</pre>
</section>


<section>
	<header>$(gettext 'Output of iwconfig')</header>
	<pre>$(iwconfig)</pre>
</section>
EOT
		;;


	*)
		# Main Network page starting with a summary
		xhtml_header

		stop_disabled=''; start_disabled=''
		if cat /sys/class/net/*/operstate | fgrep -q up; then
			start_disabled='disabled'
		else
			stop_disabled='disabled'
		fi

		cat <<EOT
<h2>$(gettext 'Networking')</h2>

<p>$(gettext 'Manage network connections and services')</p>

<form action="index.cgi" id="indexform"></form>

<form id="mainform"><!--
	--><button name="start"   data-icon="start"   $start_disabled>$(gettext 'Start'  )</button><!--
	--><button name="stop"    data-icon="stop"    $stop_disabled >$(gettext 'Stop'   )</button><!--
	--><button name="restart" data-icon="restart" $stop_disabled >$(gettext 'Restart')</button>
</form>
<div class="float-right"><!--
	-->$(gettext 'Configuration:')<!--
	--><button form="indexform" name="file" value="/etc/network.conf" data-icon="conf">network.conf</button><!--
	--><button form="mainform" name="eth" data-icon="eth">Ethernet</button><!--
	--><button form="mainform" name="wifi" data-icon="wifi">Wireless</button>
</div>


<section>
	<header>$(gettext 'Network interfaces')</header>
	$(list_network_interfaces)
</section>


<section>
	<header id="hosts">$(gettext 'Hosts')</header>
	<pre>$(cat /etc/hosts)</pre>
	<footer>
		<form action="index.cgi">
			<input type="hidden" name="file" value="/etc/hosts"/>
			<button name="action" value="edit" data-icon="edit">$(gettext 'Edit')</button>
		</form>
	</footer>
</section>


<section>
	<header>$(gettext 'Hostname')</header>
	<footer>
		<form>
			<!-- was: name="hostname"; please don't use 'name' in name: unwanted webkit styling -->
			<input type="text" name="host" value="$(cat /etc/hostname)"/><!--
			--><button type="submit" data-icon="ok">$(gettext 'Change')</button>
		</form>
	</footer>
</section>


<section>
	<header id="ifconfig">$(gettext 'Output of ifconfig')</header>
	<pre>$(ifconfig)</pre>
</section>


<section>
	<header id="routing">$(gettext 'Routing table')</header>
	<pre>$(route -n)</pre>
</section>


<section>
	<header id="dns">$(gettext 'Domain name resolution')</header>
	<pre>$(cat /etc/resolv.conf)</pre>
</section>


<section>
	<header id="arp">$(gettext 'ARP table')</header>
	<pre>$(arp)</pre>
</section>


<section>
	<header id="connections">$(gettext 'IP Connections')</header>
	<pre>$(netstat -anp 2>/dev/null | sed -e '/UNIX domain sockets/,$d' \
-e 's#\([0-9]*\)/#<a href="boot.cgi?daemons=pid=\1">\1</a>/#')</pre>
</section>
EOT
		;;
esac

xhtml_footer
exit 0
