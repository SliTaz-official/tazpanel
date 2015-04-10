#!/bin/sh
#
# Boot CGI script - All what happens before login (grub, rcS, slim)
#
# Copyright (C) 2011-2015 SliTaz GNU/Linux - BSD License
#


# Common functions from libtazpanel and source main boot config file.

. lib/libtazpanel
. /etc/rcS.conf
get_config
header

TITLE=$(_ 'TazPanel - Boot')


# Print last 40 lines of given file with "more" link

loghead() {
	case $2 in
		htmlize) tail -n40 $1 | htmlize;;
		*)       tail -n40;;
	esac
	[ $(wc -l < $1) -gt 40 ] && cat <<EOT
<hr/><a data-icon="view" href="index.cgi?file=$1">$(_ 'Show more...')</a>
EOT
}


#
# Commands
#

case " $(GET) " in
	*\ syslog\ *)
		logtype="$(GET syslog)"
		[ "$logtype" == "syslog" ] && logtype=messages
		xhtml_header
		cat <<EOT
<h2>$(_ 'System logs')</h2>

<ul id="tabs">
EOT
		for i in $(sed '/var\/log/!d;s|.*/log/||' /etc/syslog.conf); do
			unset act
			[ "$i" == "$logtype" ] && act=' class="active"'
			cat <<EOT
	<li$act><a href="?syslog=$i" title="$(sed "/$i$/!d;s/[\t ].*//" /etc/syslog.conf)">$i</a></li>
EOT
		done
		cat <<EOT
</ul>

<section>
	<div>
		<pre>$(syntax_highlighter kernel < /var/log/$logtype | \
					   loghead /var/log/$logtype)</pre>
	</div>
</section>
EOT
		;;
	*\ log\ *)
		unset actboot actslim actxlog actkernel colors
		case "$(GET log)" in
			boot)
				actboot=' class="active"'
				output="$(filter_taztools_msgs < /var/log/boot.log)"
				colors=' class="term log"';;
			slim)
				actslim=' class="active"'
				output="$(loghead /var/log/slim.log htmlize)" ;;
			xlog)
				actxlog=' class="active"'
				output="$(syntax_highlighter xlog < /var/log/Xorg.0.log | loghead /var/log/Xorg.0.log)" ;;
			*)
				actkernel=' class="active"'
				output="$(syntax_highlighter kernel < /var/log/dmesg.log | loghead /var/log/dmesg.log)" ;;
		esac
		xhtml_header
		cat <<EOT
<h2>$(_ 'Boot log files')</h2>

<ul id="tabs">
	<li$actkernel><a href="?log=kernel">$(_ 'Kernel messages')</a></li>
	<li$actboot  ><a href="?log=boot"  >$(_ 'Boot scripts'   )</a></li>
	<li$actxlog  ><a href="?log=xlog"  >$(_ 'X server'       )</a></li>
	<li$actslim  ><a href="?log=slim"  >$(_ 'X session'      )</a></li>
</ul>

<section>
	<div>
		<pre$colors>$output</pre>
	</div>
</section>
EOT
		;;


	*\ daemons\ *)
		#
		# Everything until user login
		#
		# Start and stop a daemon.
		# (I think we don't need a 'restart' since 2 clicks and you are done)
		. /etc/rcS.conf
		xhtml_header

		cat <<EOT
<h2>$(_ 'Manage daemons')</h2>

<p>$(_ 'Check, start and stop daemons on SliTaz')</p>
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
				ps ww | sed 1q
				for i in $(echo ${daemon#pid=} | sed 's/%20/ /g'); do
					ps ww | sed "/^ $i /!d"
				done
				echo "</pre>" ;;
		esac

		# Daemon list
		cat <<EOT
<section>
	<table class="zebra wide daemons">
		<thead>
			<tr>
				<td>$(_ 'Name')</td>
				<td>$(_ 'Description')</td>
				<td>$(_ 'Configuration')</td>
				<td>$(_ 'Status')</td>
				<td>$(_ 'Action')</td>
				<td>$(_ 'PID')</td>
			</tr>
		</thead>
		<tbody>
EOT
		cd /etc/init.d
		list="$(ls | sed -e /.sh/d -e /rc./d -e /RE/d -e /daemon/d -e /firewall/d)"
		for name in $list; do
			unset pkg pid status SHORT_DESC boot cfg
			echo '<tr>'
			# Name
			echo "<td>$name</td>"
			# First check if daemon is started at boottime
			[ echo "RUN_DAEMONS" | fgrep $name ] && boot="on boot"
			# Standard SliTaz busybox daemons and firewall
			echo -n "<td>"
			grep -qi "^${name}_OPTIONS=" /etc/daemons.conf && cfg="options|$cfg"
			for i in /etc/slitaz /etc /etc/$name ; do
				[ -s $i/$name.conf ] && cfg="edit::$i/$name.conf|$cfg"
			done
			[ -n "$(which $name)" ] && cfg="man|help|$cfg"
			case "$name" in
				firewall)
					_ 'SliTaz Firewall with iptable rules' ;;
				httpd)
					_ 'Small and fast web server with CGI support' ;;
				ntpd)
					_ 'Network time protocol daemon' ;;
				ftpd)
					cfg="man|help|edit::/etc/inetd.conf"
					_ 'Anonymous FTP server' ;;
				udhcpd)
					_ 'Busybox DHCP server' ;;
				syslogd|klogd)
					_ 'Linux Kernel log daemon' ;;
				crond)
					# FIXME crontab
					_ 'Execute scheduled commands' ;;
				dnsd)
					cfg="man|help|edit|options::-d"
					_ 'Small static DNS server daemon' ;;
				tftpd)
					cfg="man|help|edit::/etc/inetd.conf"
					_ 'Transfer a file on tftp request' ;;
				inetd)
					_ 'Listen for network connections and launch programs' ;;
				zcip)
					cfg="man|help|edit:Script:/etc/zcip.script|options::eth0 /etc/zcip.script"
					_ 'Manage a ZeroConf IPv4 link-local address' ;;
				*)
					# Description from receipt
					[ -d "$LOCALSTATE/installed/$name" ] && pkg=$name
					[ -d "$LOCALSTATE/installed/${name%d}" ] && pkg=${name%d}
					[ -d "$LOCALSTATE/installed/${name}-pam" ] && pkg=${name}-pam
					if [ "$pkg" ]; then
						unset SHORT_DESC TAZPANEL_DAEMON
#FIXME $PKGS_DB
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
			# Dbus
			[ -f /var/run/${name}/pid ] && pid=$(cat /var/run/${name}/pid)
			# Apache
			[ "$name" = "apache" ] && pid=$(cat /var/run/$name/httpd.pid)
			# Pidof works for many daemons
			[ "$pid" ] || pid=$(pidof $name)

			echo -n "<td style='white-space: nowrap'>"
			if [ -n "$cfg" ]; then
				IFS="|"
				for i in $cfg ; do
					IFS=":"
					set -- $i
					case "$1" in
					edit)
						cat <<EOT
<a href="index.cgi?file=${3:-/etc/$name.conf}&amp;action=edit" title="${2:-$name Configuration}" data-img="conf"></a>
EOT
						;;
					options)
						key=$(echo -n $name | tr [a-z] [A-Z])_OPTIONS
						cat <<EOT
<a href="index.cgi?file=/etc/daemons.conf&amp;action=setvar&amp;var=$key&amp;default=$3" title="${2:-$key}" data-img="opt"></a>
EOT
						;;
					man)
						cat <<EOT
<a href="index.cgi?exec=man ${3:-$name}&amp;back=boot.cgi%3Fdaemons" title="${2:-$name Manual}" data-img="man"></a>
EOT
						;;
					help)
						help='--help'
						case $name in
							cupsd|dropbear|gpm|slim|wpa_supplicant) help='-h'
						esac
						cat <<EOT
<a href="index.cgi?exec=$(which ${3:-$name}) $help&amp;back=boot.cgi%3Fdaemons" title="${2:-$name Help}" data-img="help"></a>
EOT
						;;
					web)	cat <<EOT
<a href="${i#$1:$2:}" title="${2:-$name website:} ${i#$1:$2:}" target="_blank" data-img="web"></a>
EOT
						;;
					esac
				done
			fi
			echo "</td>"
			if [ "$pid" ]; then
				cat <<EOT
<td><span title="$(_ 'Started')" data-img="on"></span></td>
<td><a href="?daemons=stop=$name" title="$(_ 'Stop')" data-img="stop"></a></td>
<td>
EOT
				for i in $pid; do
					cat <<EOT
<a href="?daemons=pid=$i">$i</a>
EOT
				done
			else
				cat <<EOT
<td><span title="$(_ 'Stopped')" data-img="off"></span></td>
<td><a href="?daemons=start=$name" title="$(_ 'Start')" data-img="start"></a></td>
<td>-----
EOT
			fi
			echo '</td></tr>'
		done
		echo '</thead></table></section>' ;;


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
		default=$(cat $GRUBMENU | grep ^default     | cut -d' ' -f2)
		timeout=$(cat $GRUBMENU | grep ^timeout     | cut -d' ' -f2)
		 splash=$(cat $GRUBMENU | grep ^splashimage | cut -d' ' -f2)
		xhtml_header
				cat <<EOT
<h2>$(_ 'GRUB Boot loader')</h2>

<p>$(_ 'The first application started when the computer powers on')</p>

<form class="wide">
	<section>
		<div>
			<input type="hidden" name="grub"/>
			<table>
				<tr><td>$(_ 'Default entry:')</td>
					<td><input type="text" name="default" value="${default##*=}"/></td></tr>
				<tr><td>$(_ 'Timeout:')</td>
					<td><input type="text" name="timeout" value="${timeout##*=}"/></td></tr>
				<tr><td>$(_ 'Splash image:')</td>
					<td><input type="text" name="splash" value="${splash##*=}" size="40"/></td></tr>
			</table>
		</div>
		<footer>
			<button type="submit" data-icon="ok">$(_ 'Change')</button>
		</footer>
	</section>
</form>

<form action="index.cgi">
	<input type="hidden" name="file" value="$GRUBMENU"/>
	<button data-icon="text">$(_ 'View or edit menu.lst')</button>
</form>


<section>
	<header>$(_ 'Boot entries')</header>
	<div>
EOT


menu=$(tail -q -n +$(grep -n ^title $GRUBMENU | head -n1 | cut -d: -f1) $GRUBMENU | \
	sed -e "s|^$||g" | \
	sed -e "s|^title|</pre></div>\n</section>\n\n<section>\n\t<header>$(_ 'Entry') #</header>\n<div><pre style=\"white-space:pre-wrap\">\0|g" | \
	sed '/^[ \t]*$/d' | \
	tail -q -n +2)"</pre>"

	entry='-1'
	echo "$menu" | while read line
	do
		if [ -n "$(echo $line | grep '#</header>')" ]; then
			entry=$(($entry + 1))
		fi
		echo $line | sed "s|#</header>|$entry</header>|"
	done

	echo '</section>'


	# Here we could check if an entry for gpxe is present if not
	# display a form to add it.
	[ -f "/boot/gpxe" ] && cat <<EOT
<section>
	<header>gPXE</header>
	<div>$(_ 'Web boot is available with gPXE')</div>
</section>
EOT
	;;


	*)
		#
		# Default content with summary
		#
		. /etc/rcS.conf
		xhtml_header
		cat <<EOT
<h2>$(_ 'Boot &amp; Start services')</h2>

<p>$(_ 'Everything that happens before user login')</p>

<form>
	<button name="log"     data-icon="logs"   >$(_ 'Boot logs')</button>
	<button name="syslog"  data-icon="logs"   >$(_ 'System logs')</button>
	<button name="daemons" data-icon="daemons" data-root>$(_ 'Manage daemons')</button>
EOT
		[ -w /boot/grub/menu.lst ] && cat <<EOT
	<button name="grub"    data-icon="grub"   >$(_ 'Boot loader')</button>
EOT
		cat <<EOT
</form>


<section>
	<header>$(_ 'Configuration files')</header>
	<form action="index.cgi" class="wide">
		<table>
			<tr><td>$(_ 'Main configuration file:') <b>rcS.conf</b></td>
				<td><button name="file" value="/etc/rcS.conf" data-icon="view">$(_ 'View')</button></td></tr>
			<tr><td>$(_ 'Login manager settings:') <b>slim.conf</b></td>
				<td><button name="file" value="/etc/slim.conf" data-icon="view">$(_ 'View')</button></td></tr>
		</table>
	</form>
</section>


<section style="overflow-x: auto">
	<header>$(_ 'Kernel cmdline')</header>
	<pre>$(cat /proc/cmdline)</pre>
</section>


<section>
	<header>
		$(_ 'Local startup commands')
		<form action="index.cgi">
			<input type="hidden" name="file" value="/etc/init.d/local.sh"/>
EOT
		[ -w /etc/init.d/local.sh ] && cat <<EOT
			<button name="action" value="edit" data-icon="edit">$(_ 'Edit')</button>
EOT
		cat <<EOT
		</form>
	</header>
	<pre>$(cat /etc/init.d/local.sh | syntax_highlighter sh)</pre>
</section>
EOT
		;;
esac

xhtml_footer
exit 0
