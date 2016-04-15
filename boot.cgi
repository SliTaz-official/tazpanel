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

TITLE=$(_ 'Boot')


# Print last 40 lines of given file with "more" link

loghead() {
	case $2 in
		htmlize) tail -n40 $1 | htmlize;;
		*)       tail -n40;;
	esac
	[ $(wc -l < $1) -gt 40 ] && cat <<EOT
<hr/><a data-icon="@view@" href="index.cgi?file=$1">$(_ 'Show more...')</a>
EOT
}


#
# Commands
#

case " $(GET) " in
	*\ syslog\ *)
		logtype="$(GET syslog)"
		[ "${logtype:-syslog}" == 'syslog' ] && logtype='messages'
		xhtml_header "$(_ 'System logs')"

		cat <<EOT
<section>
	<header>
		$(_ 'System logs')
EOT

		edit_button /etc/syslog.conf syslog.conf

		cat <<EOT
	</header>

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

	<pre style="overflow-x: auto">$(syntax_highlighter kernel < /var/log/$logtype | \
		loghead /var/log/$logtype)</pre>
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

		xhtml_header "$(_ 'Boot log files')"
		cat <<EOT
<ul id="tabs">
	<li$actkernel><a href="?log=kernel">$(_ 'Kernel messages')</a></li>
	<li$actboot  ><a href="?log=boot"  >$(_ 'Boot scripts'   )</a></li>
	<li$actxlog  ><a href="?log=xlog"  >$(_ 'X server'       )</a></li>
	<li$actslim  ><a href="?log=slim"  >$(_ 'X session'      )</a></li>
</ul>

<section>
	<div>
		<pre$colors style="overflow-x: auto">$output</pre>
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
		xhtml_header "$(_ 'Manage daemons')"

		cat <<EOT
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
				for j in $i/$name.conf $i/${name}d.conf ; do
					[ -s $j ] && cfg="edit::$j|$cfg"
				done
			done
			[ -n "$(which $name)" ] && cfg="man|help|$cfg"
			case "$name" in
				firewall)
					_ 'SliTaz Firewall with iptables rules' ;;
				httpd)
					_ 'Small and fast web server with CGI support' ;;
				ntpd)
					cfg="man|help|edit::/etc/ntp.conf|options"
					_ 'Network time protocol daemon' ;;
				ftpd)
					cfg="man|help|edit::/etc/inetd.conf"
					_ 'Anonymous FTP server' ;;
				udhcpd)
					cfg="man|help|edit|options"
					_ 'Busybox DHCP server' ;;
				syslogd|klogd)
					cfg="man|help|edit::/etc/syslog.conf|options"
					_ 'Linux Kernel log daemon' ;;
				crond)
					# FIXME crontab
					_ 'Execute scheduled commands' ;;
				dnsd)
					cfg="man|help|edit|options::-d"
					_ 'Small static DNS server daemon' ;;
				tftpd)
					cfg="man|help|edit::/etc/inetd.conf|options"
					_ 'Transfer a file on tftp request' ;;
				lpd)
					cfg="man|help|options"
					_ 'Printer daemon' ;;
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
			pidfile=$(find /run /var/run -maxdepth 2 -name *$name*.pid)
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
<a href="index.cgi?file=${3:-/etc/$name.conf}&amp;action=edit" title="${2:-$name configuration} in ${3:-/etc/$name.conf}" data-img="@conf@"></a>
EOT
						;;
					options)
						key=$(echo -n $name | tr [a-z] [A-Z])_OPTIONS
						cat <<EOT
<a href="index.cgi?file=/etc/daemons.conf&amp;action=setvar&amp;var=$key&amp;default=$3" title="${2:-$key}" data-img="@opt@"></a>
EOT
						;;
					man)
						cat <<EOT
<a href="index.cgi?exec=man ${3:-$name}&amp;back=boot.cgi%3Fdaemons" title="${2:-$name Manual}" data-img="@man@"></a>
EOT
						;;
					help)
						help='--help'
						case $name in
							cupsd|dropbear|gpm|slim|wpa_supplicant) help='-h'
						esac
						cat <<EOT
<a href="index.cgi?exec=$(which ${3:-$name}) $help&amp;back=boot.cgi%3Fdaemons" title="${2:-$name Help}" data-img="@help@"></a>
EOT
						;;
					web)	cat <<EOT
<a href="${i#$1:$2:}" title="${2:-$name website:} ${i#$1:$2:}" target="_blank" data-img="@web@"></a>
EOT
						;;
					esac
				done
			fi
			echo "</td>"
			if [ "$pid" ]; then
				cat <<EOT
<td><span title="$(_ 'Started')" data-img="@on@"></span></td>
<td><a href="?daemons=stop=$name" title="$(_ 'Stop')" data-img="@stop@"></a></td>
<td>
EOT
				for i in $pid; do
					cat <<EOT
<a href="?daemons=pid=$i">$i</a>
EOT
				done
			else
				cat <<EOT
<td><span title="$(_ 'Stopped')" data-img="@off@"></span></td>
<td><a href="?daemons=start=$name" title="$(_ 'Start')" data-img="@start@"></a></td>
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
		default=$(grep ^default     $GRUBMENU | cut -d' ' -f2)
		timeout=$(grep ^timeout     $GRUBMENU | cut -d' ' -f2)
		 splash=$(grep ^splashimage $GRUBMENU | cut -d' ' -f2)

		xhtml_header "$(_ 'GRUB Boot loader')"
				cat <<EOT
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
			<button type="submit" data-icon="@ok@">$(_ 'Change')</button>
		</footer>
	</section>
</form>

<form action="index.cgi">
	<input type="hidden" name="file" value="$GRUBMENU"/>
	<button data-icon="@text@">$(_ 'View or edit menu.lst')</button>
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


	*\ iso\ *)
		xhtml_header
		iso=$(POST iso); [ -s "$iso" ] || unset iso
		action=$(POST action); [ "$action" ] || action=$(GET action)
		workdir=$(POST workdir)
		[ -d $workdir ] || workdir=$(dirname $workdir)
		[ -w $workdir -a "$workdir" ] || workdir=/tmp

		echo "<h2>$(_ 'ISO mine')</h2>"

		[ "$iso" ] || msg err "$(_ 'Invalid ISO image.')"

		if [ "$iso" -a "$action" -a "$action" != "nop" ]; then
			case "$action" in
				install*) dev=$(POST instdev) ;;
				*) dev=$(POST usbkeydev) ;;
			esac
			cd $workdir
			cat <<EOT
<section>
<pre>
$(taziso $iso $action $dev 2>&1 | htmlize)
</pre>
</section>
EOT
		fi
		cat <<EOT
<section>
<form method="post" action="?iso" class="wide">
<table>
	<tr><td>$(_ 'ISO image file full path')
			<span data-img="@info@" title="$(_ 'set /dev/cdrom for a physical CD-ROM')"></span>
		</td>
		<td>$(file_chooser "iso" "$iso")</td></tr>
	<tr><td>$(_ 'Working directory')</td>
		<td>$(dir_chooser "workdir" "$workdir")</td></tr>
		</td></tr>
	<tr><td>$(_ 'Target partition')
			<span data-img="@info@" title="$(_ 'For hard disk installation only. Will create /slitaz tree and keep other files. No partitioning and no formatting.')"></span>
		</td>
		<td><select name="instdev">
			<option value="/dev/null">$(_ 'Choose a partition (optional)')</option>
EOT
		blkid | grep -iE "(msdos|vfat|ntfs|ext[234]|xfs|btrfs)" | \
		sed -e 's|[A-Z]*ID="[^"]*"||g;s| SEC[^ ]*||;s|LABEL=||;s|:||' \
		    -e 's|TYPE="\([^"]*\)"|\1|;s|/dev/||' | \
		while read dev label type; do
			echo -n "<option value=\"/dev/$dev\">/dev/$dev $label $type "
			echo "$(blk2h < /sys/block/${dev:0:3}/$dev/size)</option>"
		done 
		cat <<EOT
			</select></td></tr>
	<tr><td>$(_ 'USB key device')
			<span data-img="@info@" title="$(_ 'For USB boot key only. Will erase the full device.')"></span>
		</td>
		<td><select name="usbkeydev">
			<option value="/dev/null">$(_ 'Choose a USB key (optional)')</option>
EOT
		grep -l 1 /sys/block/*/removable | \
		sed 's|/sys/block/\(.*\)/removable|\1|' | while read dev; do
			grep -qs 1 /sys/block/$dev/ro && continue
			[ -d /sys/block/$dev/device/scsi_disk ] || continue
			echo -n "<option value=\"/dev/$dev\">/dev/$dev "
			echo -n "$(blk2h < /sys/block/$dev/size) "
			echo -n "$(cat /sys/block/$dev/device/model 2>/dev/null) "
			blkid | grep $dev | sed '/LABEL=/!d;s/.*LABEL="\([^"]*\).*/"\1"/;q'
			echo "</option>"
		done
		cat <<EOT
			</select></td></tr>
</table>
<footer>
EOT

		if [ "$iso" ]; then
			cat <<EOT
<select name="action">
	<option value="nop">$(_ 'Choose an action')</option>
	$(taziso $iso list | sed -e \
		's/"\(.*\)"[\t ]*"\(.*\)"/<option value="\1\">\2<\/option>/' -e \
		"s|value=\"$action\"|& selected|")
</select>
EOT
		elif [ "$action" ]; then
			cat <<EOT
<input type="hidden" name="action" value="$action" />
EOT
		fi

		cat <<EOT
	<button data-icon="@cd@" name="mine">$(_ 'Mine')</button>
</footer>
</form>
</section>
EOT
		;;


	*)
		#
		# Default content with summary
		#
		. /etc/rcS.conf
		xhtml_header "$(_ 'Boot &amp; Start services')"
		cat <<EOT
<p>$(_ 'Everything that happens before user login')</p>

<form>
	<button name="log"     data-icon="@logs@">$(_ 'Boot logs')</button>
	<button name="syslog"  data-icon="@logs@">$(_ 'System logs')</button>
	<button name="daemons" data-icon="@daemons@" data-root>$(_ 'Manage daemons')</button>
EOT
		[ "$REMOTE_USER" == "root" -a -x /usr/bin/taziso ] && cat <<EOT
	<button name="iso"     data-icon="@cd@">$(_ 'ISO mine')</button>
EOT
		[ -w /boot/grub/menu.lst ] && cat <<EOT
	<button name="grub"    data-icon="@grub@">$(_ 'Boot loader')</button>
EOT
		cat <<EOT
</form>


<section>
	<header>$(_ 'Configuration files')</header>
	<form action="index.cgi" class="wide">
		<table>
			<tr><td>$(_ 'Main configuration file:') <b>rcS.conf</b></td>
				<td><button name="file" value="/etc/rcS.conf" data-icon="@view@">$(_ 'View')</button></td></tr>
			<tr><td>$(_ 'Login manager settings:') <b>slim.conf</b></td>
				<td><button name="file" value="/etc/slim.conf" data-icon="@view@">$(_ 'View')</button></td></tr>
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
		$(edit_button /etc/init.d/local.sh)
	</header>
	<pre><code class="language-bash">$(htmlize < /etc/init.d/local.sh)</code></pre>
</section>
EOT
		;;
esac

xhtml_footer
exit 0
