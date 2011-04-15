#!/bin/sh
#
# Boot CGI script - All what happens before login (grub, rcS, slim)
#
# Copyright (C) 2011 SliTaz GNU/Linux - GNU gpl v3
#

# Common functions from libtazpanel and source main boot config file.
. lib/libtazpanel
. /etc/rcS.conf
header
get_config

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel'
export TEXTDOMAIN

TITLE="- Hardware"

#
# Commands
#

case " $(GET) " in
	*\ daemons\ *)
		#
		# Everything until user login
		#
		# Start and stop a daemon. I think we dont need restart since 2 
		# clicks and you are done
		daemon=$(GET daemons)
		case "$daemon" in
			start=*)
				sleep 1
				/etc/init.d/${daemon#start=} start | log ;;
			stop=*)
				/etc/init.d/${daemon#stop=} stop | log ;;
		esac
		. /etc/rcS.conf
		TITLE="- Boot"
		xhtml_header
		
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Manage daemons"`</h2>
	<p>
		`gettext "Check, start and stop daemons on SliTaz"` 
	</p>
</div>
EOT
		# Demon list
		table_start
		cat << EOT
<thead>
	<tr>
		<td>`gettext "Name"`</td>
		<td>`gettext "Description"`</td>
		<td>`gettext "Status"`</td>
		<td>`gettext "Action"`</td>
		<td>`gettext "PID"`</td>
	</tr>
</thead>
EOT
		cd /etc/init.d
		list="`ls | sed -e /.sh/d -e /rc./d -e /RE/d -e /daemon/d \
			-e /firewall/d`"
		for name in $list
		do
			pkg=""
			pid=""
			status=""
			SHORT_DESC=""
			echo '<tr>'
			# Name
			echo "<td>$name</td>"
			# First check if daemon is started at bootime
			[ echo "RUN_DAEMONS" | fgrep $name ] && boot="on boot"
			# Standard SliTaz busybox daemons and firewall
			case "$name" in
				firewall)
					gettext "<td>SliTaz Firewall with iptable rules</td>" ;;
				httpd)
					gettext "<td>Small and fast web server with CGI support</td>" ;;
				ntpd)
					gettext "<td>Network time protocol daemon</td>" ;;
				ftpd)
					gettext "<td>Anonymous FTP server</td>" ;;
				udhcpd)
					gettext "<td>Busybox DHCP server</td>" ;;
				syslogd|klogd)
					gettext "<td>Linux Kernel log daemon</td>" ;;
				crond)
					gettext "<td>Execute scheduled commands</td>" ;;
				dnsd)
					gettext "<td>Small static DNS server daemon</td>" ;;
				tftpd)
					gettext "<td>Transfer a file on tftp request</td>" ;;
				inetd)
					gettext "<td>Listen for network connections and launch programs</td>" ;;
				zcip)
					gettext "<td>Manage a ZeroConf IPv4 link-local address</td>" ;;
				*)
					# Descrition from receipt
					[ -d "$LOCALSTATE/installed/$name" ] && pkg=$name
					[ -d "$LOCALSTATE/installed/${name%d}" ] && pkg=${name%d}
					[ -d "$LOCALSTATE/installed/${name}-pam" ] && pkg=${name}-pam
					if [ "$pkg" ]; then
						. $LOCALSTATE/installed/$pkg/receipt
						echo "<td>$SHORT_DESC</td>"
					else
						echo "<td>----</td>"
					fi ;;
			esac
			# Attemp to get daemon status
			pidfile=`find /var/run -name *$name*.pid`
			[ "$pidfile" ] && pid=`cat $pidfile`
			# dbus
			[ -f /var/run/${name}/pid ] && pid=`cat /var/run/${name}/pid`
			# apache
			[ "$name" = "apache" ] && pid=`cat /var/run/$name/httpd.pid`
			# Pidof works for many daemon
			[ "$pid" ] || pid=`pidof $name`
			if [ "$pid" ]; then
				echo "<td><img src='$IMAGES/started.png' /></td>"
				echo "<td><a href='$SCRIPT_NAME?daemons=stop=$name'>
				<img src='$IMAGES/stop.png' /></a></td>"
				echo "<td>$pid</td>"
			else
				echo "<td>-</td>"
				echo "<td><a href='$SCRIPT_NAME?daemons=start=$name'>
					<img src='$IMAGES/start.png' /></a></td>"
				echo "<td>-----</td>"
			fi
			echo '</tr>'
		done
		table_end ;;
	*)
		#
		# Default content with summary
		#
		. /etc/rcS.conf
		TITLE="- Boot"
		xhtml_header
		
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Boot &amp; Start services"`</h2>
	<p>
		`gettext "Everything that happens before user login"` 
	</p>
</div>
<div>
	<a class="button" href="$SCRIPT_NAME?daemons">Manage daemons</a>
</div>

<h3>`gettext "Configuration files"`</h3>
<ul>
	<li>`gettext "Main configuration file:"`
		<a href="index.cgi?file=/etc/rcS.conf">rcS.conf</a></li>
	<li>`gettext "Grub menu:"`
		<a href="index.cgi?file=/boot/grub/menu.lst">menu.lst</a></li>
	<li>`gettext "Login manager settings:"`
		<a href="index.cgi?file=/etc/slim.conf">slim.conf</a></li>
</ul>

<h3>`gettext "Kernel cmdline"`</h3>
<pre>
`cat /proc/cmdline`
</pre>
<h3>`gettext "Local startup commands"`</h3>
<pre>
$(cat /etc/init.d/local.sh | syntax_highlighter sh)
</pre>
<a class="button" href="index.cgi?file=/etc/init.d/local.sh&amp;action=edit">
<img src="$IMAGES/edit.png" />$(gettext "Edit script")</a>
EOT
		;;
esac

xhtml_footer
exit 0
