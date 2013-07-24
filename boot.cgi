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

TITLE=$(gettext 'TazPanel - Boot')

#
# Commands
#

case " $(GET) " in
	*\ log\ *)
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>$(gettext 'Boot log files')</h2>
</div>
<div>
	<a class="button" href="#kernel">
		<img src="$IMAGES/tux.png" />$(gettext 'Kernel messages')</a>
	<a class="button" href="#boot">$(gettext 'Boot scripts')</a>
	<a class="button" href="#slim">$(gettext 'X server')</a>
</div>

	<h3 id="kernel">$(gettext 'Kernel messages')</h3>

	<pre>$(cat /var/log/dmesg.log | syntax_highlighter kernel)</pre>

	<h3 id="boot">$(gettext 'Boot scripts')</h3>

	<pre>$(cat /var/log/boot.log | filter_taztools_msgs)</pre>

	<h3 id="slim">$(gettext 'X server')</h3>

	<pre>
$(tail -n 40 /var/log/slim.log | htmlize)
<hr /><a href="/index.cgi?file=/var/log/slim.log">$(gettext 'Show more...')</a>
</pre>
EOT
		;;
	*\ daemons\ *)
		#
		# Everything until user login
		#
		# Start and stop a daemon. I think we don't need a restart since 2
		# clicks and you are done
		. /etc/rcS.conf
		xhtml_header

		cat << EOT
<div id="wrapper">
	<h2>$(gettext 'Manage daemons')</h2>
	<p>$(gettext 'Check, start and stop daemons on SliTaz')</p>
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
		# Daemon list
		table_start
		cat << EOT
<thead>
	<tr>
		<td>$(gettext 'Name')</td>
		<td>$(gettext 'Description')</td>
		<td>$(gettext 'Configuration')</td>
		<td>$(gettext 'Status')</td>
		<td>$(gettext 'Action')</td>
		<td>$(gettext 'PID')</td>
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
			echo -n "<td>"
			cfg=""
			grep -qi "^${name}_OPTIONS=" /etc/daemons.conf && cfg="options|$cfg"
			for i in /etc/slitaz /etc /etc/$name ; do
				[ -s $i/$name.conf ] && cfg="edit::$i/$name.conf|$cfg"
			done
			[ -n "$(which $name)" ] && cfg="man|help|$cfg"
			case "$name" in
				firewall)
					gettext 'SliTaz Firewall with iptable rules' ;;
				httpd)
					gettext 'Small and fast web server with CGI support' ;;
				ntpd)
					gettext 'Network time protocol daemon' ;;
				ftpd)
					cfg="man|help|edit::/etc/inetd.conf"
					gettext 'Anonymous FTP server' ;;
				udhcpd)
					gettext 'Busybox DHCP server' ;;
				syslogd|klogd)
					gettext 'Linux Kernel log daemon' ;;
				crond)
					# FIXME crontab
					gettext 'Execute scheduled commands' ;;
				dnsd)
					cfg="man|help|edit|options::-d"
					gettext 'Small static DNS server daemon' ;;
				tftpd)
					cfg="man|help|edit::/etc/inetd.conf"
					gettext 'Transfer a file on tftp request' ;;
				inetd)
					gettext 'Listen for network connections and launch programs' ;;
				zcip)
					cfg="man|help|edit:Script:/etc/zcip.script|options::eth0 /etc/zcip.script"
					gettext 'Manage a ZeroConf IPv4 link-local address' ;;
				*)
					# Description from receipt
					[ -d "$LOCALSTATE/installed/$name" ] && pkg=$name
					[ -d "$LOCALSTATE/installed/${name%d}" ] && pkg=${name%d}
					[ -d "$LOCALSTATE/installed/${name}-pam" ] && pkg=${name}-pam
					if [ "$pkg" ]; then
						unset SHORT_DESC TAZPANEL_DAEMON
						. $LOCALSTATE/installed/$pkg/receipt
						echo -n "$SHORT_DESC"
						cfg="${TAZPANEL_DAEMON:-$cfg|web::$WEB_SITE}"
					else
						echo -n "----"
					fi ;;
			esac
			echo "</td>"
			# Attempt to get daemon status
			pidfile=$(find /var/run -name *$name*.pid)
			[ "$pidfile" ] && pid=$(cat $pidfile)
			# dbus
			[ -f /var/run/${name}/pid ] && pid=$(cat /var/run/${name}/pid)
			# apache
			[ "$name" = "apache" ] && pid=$(cat /var/run/$name/httpd.pid)
			# Pidof works for many daemons
			[ "$pid" ] || pid=$(pidof $name)
			echo -n "<td>"
			if [ "$cfg" ]; then
				IFS="|"
				for i in $cfg ; do
					IFS=":"
					set -- $i
					case "$1" in
					edit)	cat <<EOT
<a href="index.cgi?file=${3:-/etc/$name.conf}&action=edit">
<img title="${2:-$name Configuration}" src="$IMAGES/edit.png" /></a>
EOT
						;;
					options)
						key=$(echo $name | tr [a-z] [A-Z])_OPTIONS
						cat <<EOT
<a href="index.cgi?file=/etc/daemons.conf&action=setvar&var=$key&default=$3">
<img title="${2:-$key}" src="$IMAGES/tux.png" /></a>
EOT
						;;
					man)	cat <<EOT
<a href="index.cgi?exec=man ${3:-$name}">
<img title="${2:-$name Manual}" src="$IMAGES/text.png" /></a>
EOT
						;;
					help)	cat <<EOT
<a href="index.cgi?exec=$(which ${3:-$name}) --help">
<img title="${2:-$name Help}" src="$IMAGES/help.png" /></a>
EOT
						;;
					web)	cat <<EOT
<a href="${i#$1:$2:}">
<img title="${2:-$name website:} ${i#$1:$2:}" src="$IMAGES/browser.png" /></a>
EOT
						;;
					esac
				done
			fi
			echo "</td>"
			if [ "$pid" ]; then
				cat << EOT
<td><img src="$IMAGES/started.png" alt="Started" title="$(gettext 'Started')" /></td>
<td><a href="$SCRIPT_NAME?daemons=stop=$name">
	<img src="$IMAGES/stop.png" alt="Stop" title="$(gettext 'Stop')" /></a></td>
<td>
EOT
				for i in $pid; do
					cat << EOT
<a href="$SCRIPT_NAME?daemons=pid=$i">$i</a>
EOT
				done
			else
				cat << EOT
<td><img src="$IMAGES/stopped.png" alt="Stopped" title="$(gettext 'Stopped')" /></td>
<td><a href="$SCRIPT_NAME?daemons=start=$name">
    <img src="$IMAGES/start.png" alt="Start" title="$(gettext 'Start')" /></a></td>
<td>-----
EOT
			fi
			echo '</td></tr>'
		done
		table_end ;;

	*\ grub\ *)
		GRUBMENU="/boot/grub/menu.lst"
		if [ "$(GET splash)" ]; then
			default=$(GET default)
			timeout=$(GET timeout)
			splash=$(GET splash)
			sed -i \
				-e s"|default .*|default $default # new|" \
				-e s"|timeout .*|timeout $timeout|" \
				-e s"|splashimage=.*|splashimage=$splash|" \
				$GRUBMENU
		fi
		default=$(cat $GRUBMENU | grep ^default | cut -d " " -f 2)
		timeout=$(cat $GRUBMENU | grep ^timeout | cut -d " " -f 2)
		splash=$(cat $GRUBMENU | grep ^splashimage | cut -d "=" -f 2)
		xhtml_header
				cat << EOT
<div id="wrapper">
	<h2>$(gettext 'GRUB Boot loader')</h2>

	<p>$(gettext 'The first application started when the computer powers on')</p>
</div>

<form method="get" action="$SCRIPT_NAME">
	<input type="hidden" name="grub" />
<table>
<tr><td>$(gettext 'Default entry:')</td>
	<td><input type="text" name="default" value="$default" /></td></tr>
<tr><td>$(gettext 'Timeout:')</td>
	<td><input type="text" name="timeout" value="$timeout" /></td></tr>
<tr><td>$(gettext 'Splash image:')</td>
	<td><input type="text" name="splash" value="$splash" size="40" /></td></tr>
</table>
	<input type="submit" value="$(gettext 'Change')" />
	<a class="button" href="index.cgi?file=$GRUBMENU">
		<img src="$IMAGES/text.png" />$(gettext 'View or edit menu.lst')</a>
</form>

<h3>$(gettext 'Boot entries')</h3>
EOT


menu=$(tail -q -n +$(grep -n ^title $GRUBMENU | head -n1 | cut -d: -f1) $GRUBMENU \
	| sed -e "s|^$||g" \
	| sed -e "s|^title|</pre></li>\n<p><strong>$(gettext 'Entry') #</strong></p>\n<pre>\0|g" \
	| sed '/^[ \t]*$/d' \
	| tail -q -n +2)"</pre>"

	entry='-1'
	echo "$menu" | while read line
	do
		if [ -n "$(echo $line | grep '#</strong>')" ]; then
			entry=$(($entry + 1))
		fi
		echo $line | sed "s|#</strong>|$entry</strong>|"
	done

	# Here we could check if an entry for gpxe is present if not
	# display a form to add it.
	[ -f "/boot/gpxe" ] && echo "<h3>gPXE</h3>" && \
		gettext 'Web boot is available with gPXE'
	;;
	*)
		#
		# Default content with summary
		#
		. /etc/rcS.conf
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>$(gettext 'Boot &amp; Start services')</h2>
	<p>$(gettext 'Everything that happens before user login')</p>
</div>
<div>
	<a class="button" href="$SCRIPT_NAME?log">
		<img src="$IMAGES/text.png" />$(gettext 'Boot logs')</a>
	<a class="button" href="$SCRIPT_NAME?daemons">
		<img src="$IMAGES/recharge.png" />$(gettext 'Manage daemons')</a>
	<a class="button" href="$SCRIPT_NAME?grub">$(gettext 'Boot loader')</a>
</div>

<h3>$(gettext 'Configuration files')</h3>
<ul>
	<li>$(gettext 'Main configuration file:')
		<a href="index.cgi?file=/etc/rcS.conf">rcS.conf</a></li>
	<li>$(gettext 'Login manager settings:')
		<a href="index.cgi?file=/etc/slim.conf">slim.conf</a></li>
</ul>

<h3>$(gettext 'Kernel cmdline')</h3>

<pre>$(cat /proc/cmdline)</pre>

<h3>$(gettext 'Local startup commands')</h3>

<pre>$(cat /etc/init.d/local.sh | syntax_highlighter sh)</pre>

<a class="button" href="index.cgi?file=/etc/init.d/local.sh&amp;action=edit">
<img src="$IMAGES/edit.png" />$(gettext 'Edit script')</a>
EOT
		;;
esac

xhtml_footer
exit 0
