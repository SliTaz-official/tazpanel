#!/bin/sh
#
# Boot CGI script - All what happens before login (grub, rcS, slim)
#
# Copyright (C) 2011 SliTaz GNU/Linux - BSD License
#

# Common functions from libtazpanel and source main boot config file.
. lib/libtazpanel
. /etc/rcS.conf
header
get_config

TITLE="- Boot"

#
# Commands
#

case " $(GET) " in
	*\ log\ *)
		xhtml_header
		
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Boot log files"`</h2>
</div>
<div>
	<a class="button" href="#kernel">
		<img src="$IMAGES/edit.png" />`gettext "kernel messages"`</a>
	<a class="button" href="#boot">
		<img src="$IMAGES/edit.png" />`gettext "boot scripts"`</a>
	<a class="button" href="#slim">
		<img src="$IMAGES/edit.png" />`gettext "X server"`</a>
</div>
	<a name="kernel"></a>
	<h3>`gettext "kernel messages"`</h3>
	<pre>
$(cat /var/log/dmesg.log)
	</pre>
	<a name="boot"></a>
	<h3>`gettext "boot scripts"`</h3>
	<pre>
$(sed 's/\[^Gm]*.//g' < /var/log/boot.log)
	</pre>
	<a name="slim"></a>
	<h3>`gettext "X server"`</h3>
	<pre>
$(cat /var/log/slim.log)
	</pre>
EOT
		;;
	*\ daemons\ *)
		#
		# Everything until user login
		#
		# Start and stop a daemon. I think we dont need restart since 2 
		# clicks and you are done
		. /etc/rcS.conf
		xhtml_header
		
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Manage daemons"`</h2>
	<p>
		`gettext "Check, start and stop daemons on SliTaz"` 
	</p>
</div>
EOT
		daemon=$(GET daemons)
		case "$daemon" in
			start=*)
				sleep 1
				/etc/init.d/${daemon#start=} start | log ;;
			stop=*)
				/etc/init.d/${daemon#stop=} stop | log ;;
			pid=*)
				echo "<pre>"
				ps ww | sed "1p;/^ *${daemon#pid=} /!d"
				echo "</pre>" ;;
		esac
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
				cat << EOT
<td><img src="$IMAGES/started.png" /></td>
<td><a href="$SCRIPT_NAME?daemons=stop=$name">
    <img src="$IMAGES/stop.png" /></a></td>
<td>
EOT
				for i in $pid; do
					cat << EOT
<a href="$SCRIPT_NAME?daemons=pid=$i">$i</a>
EOT
				done
			else
				cat << EOT
<td>-</td>
<td><a href="$SCRIPT_NAME?daemons=start=$name">
    <img src="$IMAGES/start.png" /></a></td>
<td>-----
EOT
			fi
			echo '</td></tr>'
		done
		table_end ;;
	*)
		#
		# Default content with summary
		#
		. /etc/rcS.conf
		xhtml_header
		
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Boot &amp; Start services"`</h2>
	<p>
		`gettext "Everything that happens before user login"` 
	</p>
</div>
<div>
	<a class="button" href="$SCRIPT_NAME?log">
		<img src="$IMAGES/edit.png" />`gettext "Boot logs"`</a>
	<a class="button" href="$SCRIPT_NAME?daemons">
		<img src="$IMAGES/recharge.png" />`gettext "Manage daemons"`</a>
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
