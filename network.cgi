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

TITLE=$(_ 'Network')

ip_forward=/proc/sys/net/ipv4/ip_forward

# Start a Wi-Fi connection

start_wifi() {
	sed -i \
		-e 's|^WIFI=.*|WIFI="yes"|' \
		-e 's|^DHCP=.*|DHCP="yes"|' \
		-e 's|^STATIC=.*|STATIC="no"|' /etc/network.conf
	ifconfig $WIFI_INTERFACE up
	iwconfig $WIFI_INTERFACE txpower auto
	/etc/init.d/network.sh restart | log

	# Sleep until connection established (max 5 seconds)
	for i in $(seq 5); do
		[ -n "$(iwconfig 2>/dev/null | fgrep Link)" ] && break
		sleep 1
	done
}


# Start an Ethernet connection

start_eth() {
	case "$(GET staticip)" in
		on) DHCP='no';  STATIC='yes';;
		*)  DHCP='yes'; STATIC='no';;
	esac

	/etc/init.d/network.sh stop | log
	sleep 2
	sed -i \
		-e "s|^INTERFACE=.*|INTERFACE=\"$(GET iface)\"|" \
		-e 's|^WIFI=.*|WIFI="no"|' \
		-e "s|^DHCP=.*|DHCP=\"$DHCP\"|" \
		-e "s|^STATIC=.*|STATIC=\"$STATIC\"|" \
		-e "s|^IP=.*|IP=\"$(GET ip)\"|" \
		-e "s|^NETMASK=.*|NETMASK=\"$(GET netmask)\"|" \
		-e "s|^GATEWAY=.*|GATEWAY=\"$(GET gateway)\"|" \
		-e "s|^DNS_SERVER=.*|DNS_SERVER=\"$(GET dns)\"|" \
		/etc/network.conf
	/etc/init.d/network.sh start | log
	. /etc/network.conf
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

				# split line into variable and value (note "=" can appear in the value)
				split($0, a, "="); variable = a[1];
				value = gensub(variable "=", "", "");

				# escape html entities
				value = gensub("\\\\", "\\\\",    "g", value);
				value = gensub("&",    "\\&amp;", "g", value);
				value = gensub("<",    "\\&lt;",  "g", value);
				value = gensub(">",    "\\&gt;",  "g", value);
				value = gensub("\"",   "\\\"",    "g", value);

				# if value was already quoted - remove \" from begin and end
				if (substr(value, 1, 2) == "\\\"")
					value = substr(value, 3, length(value) - 4);

				# output in form: variable:"escaped value"
				printf "%s:\"%s\"", variable, value;
			}
		}
		if (network == 1 && $0 ~ "}") { printf "}"; network = 0; next; }
	}
	END {print "\n];"}
	' /etc/wpa/wpa.conf | sed 's|\t||g;'
}


# Waiting for network link up

wait_up() {
	for i in $(seq 5); do
		[ -z "$(cat /sys/class/net/*/operstate | fgrep up)"] && sleep 1
	done
}

select_if() {
	echo '<select name="interface">'
	for i in $(ls /sys/class/net); do
		grep -qs 1 /sys/class/net/$i/carrier &&
		echo "<option>$i"
	done
	echo '</select>'
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
	*\ start_wifi\ *)
		start_wifi ;;
	*\ start_eth\ *)
		start_eth ;;
	*\ dowakeup\ *)
		mac="$(GET macwakup)"
		unset pass
		[ "$(GET macpass)" ] && pass="-p $(GET macpass)"
		if [ "$mac" ]; then
			ether-wake $(GET iface) $mac $pass
		else
			ether-wake -b $(GET iface) $pass
		fi
		;;
	*\ hostname\ *)
		hostname="$(GET hostname)"
		echo $(_ 'Changed hostname: %s' "$hostname") | log
		echo "$hostname" > /etc/hostname;;
	*\ rmarp\ *)
		arp -d $(urldecode "$(GET entry)") ;;
	*\ addarp\ *)
		arp -i $(GET interface) -s $(GET ip) $(GET mac) ;;
	*\ proxyarp\ *)
		arp -i $(GET interface) -Ds $(GET ip) $(GET interface) pub ;;
	*\ toggleipforward\ *)
		echo $((1 - $(cat $ip_forward))) > $ip_forward ;;
esac

case " $(POST) " in
	*\ connect_wifi\ *)
		# Connect to a Wi-Fi network
		/etc/init.d/network.sh stop | log
		password="$(POST password)"

		# Escape special characters to use with sed substitutions
		password="$(echo -n "$password" | sed 's|\\|\\\\|g; s|&|\\\&|g' | sed "s|'|'\"'\"'|g")"

		sed -i \
			-e "s|^WIFI_ESSID=.*|WIFI_ESSID=\"$(POST essid)\"|" \
			-e "s|^WIFI_BSSID=.*|WIFI_BSSID=\"$(POST bssid)\"|" \
			-e "s|^WIFI_KEY_TYPE=.*|WIFI_KEY_TYPE=\"$(POST keyType)\"|" \
			-e "s|^WIFI_KEY=.*|WIFI_KEY='$password'|" \
			-e "s|^WIFI_EAP_METHOD=.*|WIFI_EAP_METHOD=\"$(POST eap)\"|" \
			-e "s|^WIFI_CA_CERT=.*|WIFI_CA_CERT=\"$(POST caCert)\"|" \
			-e "s|^WIFI_CLIENT_CERT=.*|WIFI_CLIENT_CERT=\"$(POST clientCert)\"|" \
			-e "s|^WIFI_IDENTITY=.*|WIFI_IDENTITY=\"$(POST identity)\"|" \
			-e "s|^WIFI_ANONYMOUS_IDENTITY=.*|WIFI_ANONYMOUS_IDENTITY=\"$(POST anonymousIdentity)\"|" \
			-e "s|^WIFI_PHASE2=.*|WIFI_PHASE2=\"$(POST phase2)\"|" \
			/etc/network.conf
		. /etc/network.conf
		start_wifi
		;;
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
		loading_msg "$(_ 'Scanning open ports...')"

		cat <<EOT
<section>
	<header>
		$(_ 'Port scanning for %s' $scan)
		$(back_button "$back" "$(_ 'Network')" "")
	</header>
	<pre>$(pscan -b $scan)</pre>
</section>
EOT
		;;


	*\ eth\ *)
		# Wired connections settings
		xhtml_header "$(_ 'Ethernet connection')"

		PAR1="size=\"20\" required"; PAR="$PAR1 pattern=\"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\""

		case "$STATIC" in
			yes) use_static='checked';;
			*)   use_static='';;
		esac

		stop_disabled=''; start_disabled=''
		if cat /sys/class/net/eth*/operstate | fgrep -q up; then
			start_disabled='disabled'
		else
			stop_disabled='disabled'
		fi

		[ -s /etc/ethers ] || echo "#01:02:03:04:05:06 mystation" > /etc/ethers
		[ -w /etc/network.conf ] && cat <<EOT
<p>$(_ "Here you can configure a wired connection using DHCP to \
automatically get a random IP or configure a static/fixed IP")</p>

<section>
	<header>$(_ 'Configuration')</header>
	<form action="index.cgi" id="indexform"></form>
	<form id="conf">
		<input type="hidden" name="eth"/>
		<div>
			<table>
				<tr><td>$(_ 'Interface')</td>
					<td><select name="iface" value="$INTERFACE" style="width:100%">
					$(cd /sys/class/net; ls -1 | awk -viface="$INTERFACE" '{
						sel = ($0 == iface) ? " selected":""
						printf "<option value=\"%s\"%s>%s", $0, sel, $0
					}')
					</select></td>
				</tr>
				<tr><td>$(_ 'Static IP')</td>
					<td><label><input type="checkbox" name="staticip" id="staticip" $use_static/>
						$(_ 'Use static IP')</td>
				</tr>
				<tr id="st1"><td>$(_ 'IP address')</td>
					<td><input type="text" name="ip"      value="$IP"         $PAR/></td>
				</tr>
				<tr id="st2"><td>$(_ 'Netmask')</td>
					<td><input type="text" name="netmask" value="$NETMASK"    $PAR/></td>
				</tr>
				<tr id="st3"><td>$(_ 'Gateway')</td>
					<td><input type="text" name="gateway" value="$GATEWAY"    $PAR/></td>
				</tr>
				<tr id="st4"><td>$(_ 'DNS server')</td>
					<td><input type="text" name="dns"     value="$DNS_SERVER" $PAR/></td>
				</tr>
				<tr><td>$(_ 'Wake up')</td>
					<td><label><input type="checkbox" name="wakeup" id="wakeup" />
						$(_ 'Wake up machines by network')</td>
				</tr>
				<tr id="wk1"><td>$(_ 'MAC address to wake up')</td>
					<td><input type="text" name="macwakup" title="$(_ 'Leave empty for a general wakeup')" $PAR/><!--
					--><button form="indexform" name="file" value="/etc/ethers" data-icon="view">$(_ 'List')</button>
					</td>
				</tr>
				<tr id="wk2"><td>$(_ 'MAC/IP address password')</td>
					<td><input type="text" name="macpass" title="$(_ 'Leave empty for a general wakeup')" $PAR/><!--
					--><button form="indexform" name="exec" value="ether-wake --help" data-icon="help">$(_ 'Help')</button>
					</td>
				</tr>
			</table>
		</div>
	</form>
	<footer><!--
		--><button form="conf" type="submit" name="start_eth" data-icon="start" $start_disabled>$(_ 'Start'  )</button><!--
		--><button form="conf" type="submit" name="stop"      data-icon="stop"  $stop_disabled >$(_ 'Stop'   )</button><!--
		--><button form="conf" type="submit" name="dowakeup"  data-icon="clock" $stop_disabled >$(_ 'Wake up')</button><!--
	--></footer>
</section>

<script type="text/javascript">
function check_change() {
	enabled = document.getElementById('staticip').checked;
	for (i = 1; i < 5; i++) {
		document.getElementById('st' + i).style.display = enabled ? '' : 'none';
	}
	enabled = document.getElementById('wakeup').checked;
	for (i = 1; i < 3; i++) {
		document.getElementById('wk' + i).style.display = enabled ? '' : 'none';
	}
}

document.getElementById('staticip').onchange = check_change;
document.getElementById('wakeup').onchange = check_change;
check_change();
</script>
EOT
		cat <<EOT
<section>
	<header>
		$(_ 'Configuration file')
EOT
		edit_button /etc/network.conf
		cat <<EOT
	</header>
	<div>$(_ "These values are the ethernet settings in the main /etc/network.conf configuration file")</div>
	<pre>$(awk '{if($1 !~ "WIFI" && $1 !~ "#" && $1 != ""){print $0}}' /etc/network.conf | syntax_highlighter conf)</pre>
</section>
EOT
		;;



	*\ wifi_list\ *)
		# Catch ESSIDs and format output.
		# We get the list of networks by Cell and without spaces.

		HIDDEN="$(_ '(hidden)')"

		cat <<EOT
<table class="wide center zebra">
	<thead>
		<tr>
			<td>$(_ 'Name')</td>
			<td>$(_ 'Signal level')</td>
			<td>$(_ 'Channel')</td>
			<td>$(_ 'Encryption')</td>
			<td>$(_ 'Status')</td>
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
					ENC_SIMPLE="$(_ 'None')"; ENC_ICON='seclo' # low
				fi

				# Connected or not connected...
				if  ifconfig $WIFI_INTERFACE | fgrep -q inet && \
					iwconfig $WIFI_INTERFACE | fgrep -q "ESSID:\"$ESSID\""; then
					status="$(_ 'Connected')"
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
		xhtml_header "$(_ 'Wireless connection')"

		. /etc/network.conf

		start_disabled=''; stop_disabled=''
		if iwconfig 2>/dev/null | grep -q 'Tx-Power=off'; then
			stop_disabled='disabled'
		else
			start_disabled='disabled'
		fi

		[ -w /etc/network.conf ] && cat <<EOT
<form>
	<input type="hidden" name="wifi"/>
	   <button name="start_wifi" data-icon="start"   $start_disabled>$(_ 'Start')</button><!--
	--><button name="stop"       data-icon="stop"    $stop_disabled >$(_ 'Stop' )</button><!--
	--><button type="submit"     data-icon="refresh" $stop_disabled >$(_ 'Scan' )</button>
</form>
EOT

		[ -w /etc/network.conf ] &&
		if [ -n "$start_disabled" ]; then
			cat <<EOT
<section id="wifiList">
	<div style="text-align: center;"><span data-icon="clock">$(_ 'Scanning wireless interface...')</span></div>
</section>

<script type="text/javascript">
	ajax('network.cgi?wifi_list', '1', 'wifiList');
	$(parse_wpa_conf)
</script>
EOT

		# Escape html characters in the WIFI_KEY
		WIFI_KEY_ESCAPED="$(echo -n "$WIFI_KEY" | sed 's|&|\&amp;|g; s|<|\&lt;|g; s|>|\&gt;|g; s|"|\&quot;|g')"

			cat <<EOT
<section>
	<header>$(_ 'Connection')</header>
	<div>
		<form method="post" action="?wifi" id="connection">
			<input type="hidden" name="connect_wifi"/>
			<input type="hidden" name="bssid" id="bssid"/>
			<table>
				<tr><td>$(_ 'Network SSID')</td>
					<td><input type="text" name="essid" value="$WIFI_ESSID" id="essid"/></td>
				</tr>

				<tr><td>$(_ 'Security')</td>
					<td><select name="keyType" id="keyType">
							<option value="NONE">$(_ 'None')</option>
							<option value="WEP" >WEP</option>
							<option value="WPA" >WPA/WPA2 PSK</option>
							<option value="EAP" >802.1x EAP</option>
						</select>
					</td>
				</tr>

				<tr class="eap">
					<td><div>$(_ 'EAP method')</div></td>
					<td><div><select name="eap" id="eap">
							<option value="PEAP">PEAP</option>
							<option value="TLS" >TLS</option>
							<option value="TTLS">TTLS</option>
							<option value="PWD" >PWD</option>
						</select>
					</div></td>
				</tr>

				<tr class="eap1">
					<td><div>$(_ 'Phase 2 authentication')</div></td>
					<td><div><select name="phase2" id="phase2">
							<option value="none"    >$(_ 'None')</option>
							<option value="pap"     >PAP</option>
							<option value="mschap"  >MSCHAP</option>
							<option value="mschapv2">MSCHAPV2</option>
							<option value="gtc"     >GTC</option>
						</select>
					</div></td>
				</tr>

				<tr class="eap1">
					<td><div>$(_ 'CA certificate')</div></td>
					<td><div><input type="text" name="caCert" id="caCert"></div></td>
				</tr>

				<tr class="eap1">
					<td><div>$(_ 'User certificate')</div></td>
					<td><div><input type="text" name="clientCert" id="clientCert"></div></td>
				</tr>

				<tr class="eap">
					<td><div>$(_ 'Identity')</div></td>
					<td><div><input type="text" name="identity" id="identity"></div></td>
				</tr>

				<tr class="eap1">
					<td><div>$(_ 'Anonymous identity')</div></td>
					<td><div><input type="text" name="anonymousIdentity" id="anonymousIdentity"></div></td>
				</tr>

				<tr class="wep wpa eap">
					<td><div>$(_ 'Password')</div></td>
					<td><div>
						<input type="password" name="password" value="$WIFI_KEY_ESCAPED" id="password"/>
						<span data-img="view" title="$(_ 'Show password')"
							onmousedown="document.getElementById('password').type='text'; return false"
							  onmouseup="document.getElementById('password').type='password'"
							 onmouseout="document.getElementById('password').type='password'"
						></span>
					</div></td>
				</tr>

			</table>
		</form>
	</div>
	<footer>
		<button form="connection" type="submit" name="wifi" data-icon="ok">$(_ 'Configure')</button>
		<button data-icon="user" onclick="shareWiFi(); popup('popup_qr', 'show');">$(_ 'Share')</button>
	</footer>
</section>

<script type="text/javascript">
function wifiSettingsChange() {
	document.getElementById('connection').className = 
		document.getElementById('keyType').value.toLowerCase() + ' ' + 
		document.getElementById('eap').value.toLowerCase();
}
document.getElementById('keyType').onchange = wifiSettingsChange;
document.getElementById('eap').onchange = wifiSettingsChange;

document.getElementById('keyType').value = "$WIFI_KEY_TYPE"; wifiSettingsChange();

function shareWiFi() {
	// S=<SSID>; T={WPA|WEP|nopass}; P=<password>; H=<hidden?>
	// Escape ":" and ";" -> "\:" and "\;"
	// No harm for regular networks marked as hidden
	var text = "WIFI:" + 
		"S:" + document.getElementById('essid').value.replace(/:/g, "\\\\:").replace(/;/g, "\\\\;") + ";" +
		"T:" + document.getElementById('keyType').value.replace("NONE", "nopass") + ";" +
		"P:" + document.getElementById('password').value.replace(/:/g, "\\\\:").replace(/;/g, "\\\\;") + ";" +
		"H:true;" +
		";";
	document.getElementById('qrimg').title = text;
	qr.image({
		image: document.getElementById('qrimg'),
		value: text,
		size: 10
	});
}
</script>

<div id="shader" class="hidden" onclick="popup('popup_qr', 'close');"></div>

<table id="popup_qr" class="hidden" onclick="popup('popup_qr', 'close')">
	<tr>
		<td style="text-align: center;">
			<div id="popup_qr_inner">
				<img id="qrimg"/><br/>
				$(_ 'Share Wi-Fi network with your friends')
			</div>
		</td>
	</tr>
</table>
EOT
		fi

		cat <<EOT
<section>
	<header>
		$(_ 'Configuration file')
EOT
		edit_button /etc/network.conf
		cat <<EOT
	</header>
	<div>$(_ "These values are the wifi settings in the main /etc/network.conf configuration file")</div>
	<pre>$(grep ^WIFI /etc/network.conf | sed 's|WIFI_KEY=.*|WIFI_KEY="********"|' | syntax_highlighter conf)</pre>
</section>


<section>
	<header>$(_ 'Output of iwconfig')</header>
	<pre>$(iwconfig)</pre>
</section>
EOT
		;;


	*\ hosts\ *)
		# Configure to use hosts as Ad blocker
		xhtml_header "$(_ 'Use hosts file as Ad blocker')"

		term=$(GET term)
		found=$(mktemp)

		# Find the hosts list
		hosts=$(echo "$QUERY_STRING&" | awk '
			BEGIN { RS="&"; FS="=" }
			$1=="host" { printf "%s ", $2 }
		')
		hosts=$(httpd -d "${hosts% }")
		# now hosts='host1 host2 ... hostn'

		if [ -n "$(GET add)" ]; then
			# Add given host

			host="$(GET add)"

			echo "0.0.0.0 $host #U" >> /etc/hosts
			echo -n '<p><span data-img="info"></span>'
			_ 'Host "%s" added to /etc/hosts.' "$host"
			echo '</p>'

		elif [ -n "$hosts" ]; then
			# Disable given hosts

			for host in $hosts; do
				sed -i "s|^0.0.0.0[ \t][ \t]*$host\$|#\0|" /etc/hosts
				sed -i "s|^0.0.0.0[ \t][ \t]*$host .*|#\0|" /etc/hosts
			done
			r=$(echo "$hosts" | tr ' ' '\n' | wc -l)
			echo -n '<p><span data-img="info"></span>'
			_p  '%d record disabled' \
				'%d records disabled' "$r"   "$r"
			echo '</p>'
		fi

		# When search term given
		if [ -z "$term" ]; then
			getdb hosts | fgrep 0.0.0.0 > "$found"
			r=$(wc -l < "$found")
			echo -n '<p><span data-img="info"></span>'
			_p  '%d record used for Ad blocking' \
				'%d records used for Ad blocking' "$r"   "$r"
		else
			getdb hosts | fgrep 0.0.0.0 | fgrep "$term" > "$found"
			r=$(wc -l < "$found")
			echo -n '<p><span data-img="info"></span>'
			_p  '%d record found for "%s"' \
				'%d records found for "%s"' "$r"   "$r" "$term"
		fi

		[ "$r" -gt 100 ] && _ ' (The list is limited to the first 100 entries.)'
		echo '</p>'

		cat <<EOT
	<section>
		<header>
			<span data-icon="list">$(_ 'Hosts')</span>
			<form id="hosts">
				<input type="hidden" name="hosts" value=""/>
				<input type="search" name="term" value="$(GET term)" results="5" autosave="hosts" autocomplete="on"/>
			</form>
		</header>
		<pre class="scroll">
EOT
		sort "$found" | head -n100 | awk '{
			printf "<label><input type=\"checkbox\" name=\"host\" value=\"%s\" form=\"hosts\"/> %s</label>\n", $2, $2;
		}'
		rm "$found"
		cat <<EOT
</pre>
		<footer>
			<button form="hosts" data-icon="delete" data-root>$(_ 'Disable selected')</button>
		</footer>
	</section>

	<section>
		<header><span data-icon="add">$(_ 'Add')</span></header>
		<form class="wide">
			<div>
				<input type="hidden" name="hosts"/>
				$(_ 'Host:')
				<input type="text" name="add"/>
				<button type="submit" data-icon="add" data-root>$(_ 'Add')</button>
			</div>
		</form>
	</section>
EOT
		;;


	*)
		# Main Network page starting with a summary
		xhtml_header "$(_ 'Manage network connections and services')"

		stop_disabled=''; start_disabled=''
		if cat /sys/class/net/*/operstate | fgrep -q up; then
			start_disabled='disabled'
		else
			stop_disabled='disabled'
		fi

		if [ ! -w '/etc/network.conf' ]; then
			start_disabled='disabled'; stop_disabled='disabled'
		fi

		cat <<EOT
<form action="index.cgi" id="indexform"></form>

<form id="mainform"><!--
	--><button name="start"   data-icon="start"   $start_disabled>$(_ 'Start'  )</button><!--
	--><button name="stop"    data-icon="stop"    $stop_disabled >$(_ 'Stop'   )</button><!--
	--><button name="restart" data-icon="restart" $stop_disabled >$(_ 'Restart')</button>
</form>

<div class="float-right"><!--
	-->$(_ 'Configuration:')<!--
	--><button form="indexform" name="file" value="/etc/network.conf" data-icon="conf">network.conf</button><!--
	--><button form="mainform" name="eth" data-icon="eth">Ethernet</button><!--
	--><button form="mainform" name="wifi" data-icon="wifi">Wireless</button>
</div>


<section>
	<header>$(_ 'Network interfaces')</header>
	$(list_network_interfaces)
	<footer>
		<input form="mainform" type="checkbox" name="opt" value="ipforward" $(
		[ "$REMOTE_USER" != 'root' ] && echo ' disabled' ;
		[ $(cat $ip_forward) -eq 1 ] && echo ' checked')/>
EOT
		_ 'forward packets between interfaces'
		[ "$REMOTE_USER" == 'root' ] && cat <<EOT
		<button form="mainform" name="toggleipforward" data-icon="ok">$(_ 'Change')</button>
EOT
		cat <<EOT
	</footer>
</section>


<section>
	<header id="hosts">$(_ 'Hosts'; edit_button /etc/hosts)</header>
	<span data-icon="info">$(r=$(getdb hosts | wc -l); 
		_p '%s record in the hosts DB' \
			'%s records in the hosts DB' "$r" \
			"$r")</span>
	<pre class="scroll">$(getdb hosts | fgrep -v 0.0.0.0)</pre>
	<footer>
		<form>
			<button name="hosts" data-icon="admin" data-root>$(_ 'Configure')</button>
			$(_ 'Use hosts file as Ad blocker')
		</form>
	</footer>
</section>


<section>
	<header>$(_ 'Hostname')</header>
	<footer>
EOT
		if [ -w '/etc/hostname' ]; then
			cat <<EOT
		<form>
			<input type="text" name="hostname" value="$(hostname)"/><!--
			--><button type="submit" data-icon="ok">$(_ 'Change')</button>
		</form>
EOT
		else
			cat /etc/hostname
		fi
		cat <<EOT
	</footer>
</section>


<section>
	<header id="ifconfig">$(_ 'Output of ifconfig')</header>
	<pre>$(ifconfig)</pre>
</section>


<section>
	<header id="routing">$(_ 'Routing table')</header>
	<pre>$(route -n)</pre>
</section>


<section>
	<header id="dns">$(_ 'Domain name resolution'; edit_button /etc/resolv.conf)</header>
	<pre>$(cat /etc/resolv.conf)</pre>
</section>


<section>
	<header id="arp">$(_ 'ARP table')</header>
EOT
		if [ "$REMOTE_USER" == "root" ]; then
			echo "<table>"
			arp -n | while read line ; do
				cat <<EOT
<form>
	<tr><td>
	<input type="hidden" name="entry" value="$(urlencode "$(echo $line | \
		sed 's/) .* on/ -i/;s/.*(//')")">
	<button type="submit" data-icon="remove" name="rmarp"></button>
	</td><td><pre>$line</pre></td></tr>
</form>
EOT
			done
			cat <<EOT
	</table>
	<footer>
		<form>
			IP <input type="text" name="ip" value="10.20.30.40" size="12" /> on $(select_if)<!--
			--><button type="submit" data-icon="upgrade" name="proxyarp">$(_ 'Proxy')</button>
			or <button type="submit" data-icon="add" name="addarp">$(_ 'Add')</button>
			 MAC <input type="text" name="mac" value="11:22:33:44:55:66" size="16" />
		</form>
EOT
		else
			echo "<pre>$(arp -n)</pre>"
		fi
		cat <<EOT
	</footer>
</section>


<section>
	<header id="connections">$(_ 'IP Connections')</header>
	<pre>$(netstat -anp 2>/dev/null | sed -e '/UNIX domain sockets/,$d' \
-e 's#\([0-9]*\)/#<a href="boot.cgi?daemons=pid=\1">\1</a>/#')</pre>
</section>

EOT
		[ "$REMOTE_USER" == "root" -a "$(which iptables-save)" ] && cat <<EOT
<section>
	<header id="iptables">$(_ 'Firewall')
		$(edit_button /etc/knockd.conf "$(_ 'Port knocker')")
	</header>
	<pre>$(iptables-save)</pre>
</section>
EOT
		
		;;
esac

xhtml_footer
exit 0
