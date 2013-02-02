#!/bin/sh
#
# Hardware part of TazPanel - Devices, drivers, printing
#
# Copyright (C) 2011 SliTaz GNU/Linux - BSD License
#

# Common functions from libtazpanel
. lib/libtazpanel
get_config
header

TITLE=$(gettext 'TazPanel - Hardware')

ktoh()
{
	k=$1
	if [ $k -lt 1024 ]; then
		echo ${k}K
		return
	fi
	k=$((($k+512)/1024))
	if [ $k -lt 1024 ]; then
		echo ${k}M
		return
	fi
	k=$((($k+512)/1024))
	if [ $k -lt 1024 ]; then
		echo ${k}G
		return
	fi
	k=$((($k+512)/1024))
	echo ${k}T
}
#
# Commands
#

case " $(GET) " in
	*\ print\ *)
		xhtml_header
		echo "<h2>TODO</h2>" ;;
	*\ detect\ *)
		# Front end for Tazhw
		# TODO: Add button to detect webcam, etc. Like in tazhw box.
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>$(gettext 'Detect hardware')</h2>
	<p>$(gettext 'Detect PCI and USB hardware')</p>
</div>

<pre>$(tazhw detect-pci | syntax_highlighter sh)</pre>

<pre>$(tazhw detect-usb | syntax_highlighter sh)</pre>
EOT
		;;
	*\ modules\ *|*\ modinfo\ *)
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>$(gettext 'Kernel modules')</h2>
	<div class="float-right">
		<form method="get" action="$SCRIPT_NAME">
			<input type="hidden" name="modules" />
			<input type="search" placeholder="$(gettext 'Modules search')" name="search" />
		</form>
	</div>
	<p>$(gettext 'Manage, search or get information about the Linux kernel modules')</p>
</div>
EOT
		# Request may be modinfo output that we want in the page itself
		get_modinfo="$(GET modinfo)"
		if [ -n "$get_modinfo" ]; then
			cat << EOT
<strong>$(eval_gettext 'Detailed information for module: $get_modinfo')</strong>

<pre>$(modinfo $get_modinfo)</pre>
EOT
		fi
		if [ -n "$(GET modprobe)" ]; then
			echo "<pre>$(modprobe -v $(GET modprobe))</pre>"
		fi
		if [ -n "$(GET rmmod)" ]; then
			echo "Removing"
			rmmod -w $(GET rmmod)
		fi
		get_search="$(GET search)"
		if [ -n "$get_search" ]; then
			eval_gettext 'Matching result(s) for: $get_search'
			echo '<pre>'
			modprobe -l | grep "$(GET search)" | while read line
			do
				name=$(basename $line)
				mod=${name%.ko.gz}
				echo "$(gettext 'Module:') <a href='$SCRIPT_NAME?modinfo=$mod'>$mod</a>"
			done
			echo '</pre>'
		fi
		cat << EOT
	$(table_start)
		<tr class="thead">
			<td>$(gettext 'Module')</td>
			<td>$(gettext 'Size')</td>
			<td>$(gettext 'Used')</td>
			<td>$(gettext 'by')</td>
		</tr>
EOT
		# Get the list of modules and link to modinfo
		lsmod | grep ^[a-z] | while read MOD SIZE USED BY
		do
			cat << EOT
		<tr>
			<td><a href="$SCRIPT_NAME?modinfo=$MOD">$MOD</a></td>
			<td>$SIZE</td>
			<td>$USED</td>
			<td>$(echo $BY | sed s/","/" "/g)</td>
		</tr>
EOT
		done
		table_end ;;
	*)
		[ -n "$(GET brightness)" ] &&
		echo -n $(GET brightness) > /sys/devices/virtual/backlight/$(GET dev)/brightness

		#
		# Default to summary with mounted filesystem, loaded modules
		#
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>$(gettext 'Drivers &amp; Devices')</h2>
	<p>$(gettext 'Manage your computer hardware')</p>
</div>
<div>
	<a class="button" href="$SCRIPT_NAME?modules">
		<img src="$IMAGES/tux.png" />$(gettext 'Kernel modules')</a>
	<a class="button" href="$SCRIPT_NAME?detect">
		<img src="$IMAGES/monitor.png" />$(gettext 'Detect PCI/USB')</a>
</div>

<div id="wrapper">
EOT
		if [ -n "$(ls /proc/acpi/battery/*/info 2> /dev/null)" ]; then
			echo "<table>"
			for dev in /proc/acpi/battery/*; do
				grep ^present $dev/info | grep -q yes || continue
				design=$(sed '/design capacity:/!d;s/[^0-9]*\([0-9]*\).*/\1/' < $dev/info)
				remain=$(sed '/remaining capacity/!d;s/[^0-9]*\([0-9]*\).*/\1/' < $dev/state)
				rate=$(sed '/present rate/!d;s/[^0-9]*\([0-9]*\).*/\1/' < $dev/state)
				full=$(sed '/last full capacity/!d;s/[^0-9]*\([0-9]*\).*/\1/' < $dev/info)
				warning=$(sed '/design capacity warning/!d;s/[^0-9]*\([0-9]*\).*/\1/' < $dev/info)
				low=$(sed '/design capacity low/!d;s/[^0-9]*\([0-9]*\).*/\1/' < $dev/info)
				state=$(sed '/charging state/!d;s/\([^:]*:[ ]\+\)\([a-z]\+\)/\2/' < $dev/state)

				rempct=$(( $remain * 100 / $full ))
				cat << EOT
<tr>
	<td><img src="$IMAGES/battery.png" />
		$(gettext 'Battery') $(grep "^battery type" $dev/info | sed 's/.*: *//')
		$(grep "^design capacity:" $dev/info | sed 's/.*: *//') </td>
	<td>$(gettext 'health') $(( (100*$full)/$design))%</td>
	<td class="meter"><meter min="0" max="$full" value="$remain" low="$low"
		high="$warning" optimum="$full"></meter>
		<span>
EOT
				case "$state" in
				"discharging")
					remtime=$(( $remain * 60 / $rate ))
					remtimef=$(printf "%d:%02d" $(($remtime/60)) $(($remtime%60)))
					eval_gettext 'Discharging $rempct% - $remtimef' ;;
				"charging")
					remtime=$(( ($full - $remain) * 60 / $rate ))
					remtimef=$(printf "%d:%02d" $(($remtime/60)) $(($remtime%60)))
					eval_gettext 'Charging $rempct% - $remtimef' ;;
				"charged")
					gettext 'Charged 100%' ;;
				esac
				echo '</span></td></tr>'
			done
			echo "</table>"
		fi

		if [ -n "$(ls /sys/devices/virtual/thermal/*/temp 2> /dev/null)" ]; then
			echo -n '<p>'; gettext 'Temperature:'
			for temp in /sys/devices/virtual/thermal/*/temp; do
				awk '{ print $1/1000 }' < $temp
			done
			echo '</p>'
		fi

		if [ -n "$(ls /sys/devices/virtual/backlight/*/brightness 2> /dev/null)" ]; then
			cat <<EOT
<form method="get" action="$SCRIPT_NAME">
EOT
			for dev in /sys/devices/virtual/backlight/*/brightness ; do
				name=$(echo $dev | sed 's|.*/backlight/\([^/]*\).*|\1|')
				cat <<EOT
<input type="hidden" name="dev" value="$name" />
$(gettext 'Brightness') \
$(sed 's/.*\.//;s/_*$//' < /sys/devices/virtual/backlight/$name/device/path):
<select name="brightness" onchange="submit();">
EOT
				max=$(cat /sys/devices/virtual/backlight/$name/max_brightness)
				for i in $(seq 0 $max); do
					echo -n "<option value=\"$i\""
					[ $i -eq $(cat /sys/devices/virtual/backlight/$name/actual_brightness) ] &&
					echo -n " selected=\"selected\""
					echo "> $(( (($i + 1) * 100) / ($max + 1) ))% </option>"
				done
				cat <<EOT
</select>
EOT
			done
			cat << EOT
</form>
EOT
		fi
		cat << EOT
</div>

<h3>$(gettext 'Filesystem usage statistics')</h3>
<pre>
EOT
		fdisk -l | fgrep Disk
		echo '</pre>'


		#
		# Disk stats and management (mount, umount, check)
		#
		device=$(GET device)
		case "$device" in
		*[\;\`\&\|\$]*) ;;
		mount\ *)
			$device $(GET mountpoint);;
		umount\ *|swapon\ *|swapoff\ *)
			$device ;;
		esac
		cat << EOT
<a name="mount">
<form method="get" action="$SCRIPT_NAME#mount">
<table class="zebra outbox">
EOT
		df_thead
		echo '<tbody>'
		blkid | sort | while read dev misc
		do
			fs=${dev%:}
			set --
			df | grep -q "^$fs " && set -- $(df -h | grep "^$fs ")
			size=$2
			used=$3
			av=$4
			pct=$5
			mp=$6
			action="mount"
			[ -n "$mp" ] && action="umount"
			type=$(blkid $fs | sed '/TYPE=/!d;s/.*TYPE="\([^"]*\).*/\1/')
			[ "$type" == "swap" ] && action="swapon"
			if grep -q "^$fs " /proc/swaps; then
				action="swapoff"
				set -- $(grep "^$fs " /proc/swaps)
				size=$(ktoh $3)
				used=$(ktoh $4)
				av=$(ktoh $(($3-$4)))
				pct=$(((100*$4)/$3))%
				mp=swap
			fi
			cat << EOT
<tr>
	<td><input type="radio" name="device" value="$action $fs" />
	    <img src="$IMAGES/harddisk.png" />${fs#/dev/}</td>
	<td>$(blkid $fs | sed '/LABEL=/!d;s/.*LABEL="\([^"]*\).*/\1/')</td>
	<td>$type</td>
	<td>$size</td>
	<td>$av</td>
EOT
		if [ -n "$pct" ]; then
			cat << EOT
	<td class="meter"><meter min="0" max="100" value="${pct%%%}" low="70"
	high="90" optimum="10"></meter>
		<span>$used - $pct</span>
	</td>
EOT
		else
			cat << EOT
	<td></td>
EOT
		fi
		cat << EOT
	<td>$mp</td>
	<td>$(blkid $fs | sed '/UUID=/!d;s/.*UUID="\([^"]*\).*/\1/')</td>
</tr>
EOT
		done
		cat << EOT
</tbody>
</table>
<input type="submit" value="mount / umount" /> -
new mount point <input type=text" name="mountpoint" value="/media/usbdisk" />
</form>
<h3>$(gettext 'Filesystems table')</h3>
<pre>
$(grep -v ^# /etc/fstab | syntax_highlighter conf)
</pre>
<a class="button" href="index.cgi?file=/etc/fstab&action=edit">
	<img src="$IMAGES/edit.png" />$(gettext 'Manual Edit')</a>
EOT


		cat << EOT
<h3>$(gettext 'System memory')</h3>
<pre>
EOT
		free -m | sed \
			-e s"#total.*\([^']\)#<span class='top'>\0</span>#"g \
			-e s"#^[A-Z-].*:\([^']\)#<span class='sh-comment'>\0</span>#"g
		cat << EOT
</pre>

<h3>lspci</h3>
<pre>
EOT
			lspci -k | sed \
			 -e s"#^[0-9].*\([^']\)#<span class='diff-at'>\0</span>#" \
			 -e s"#use: \(.*\)#use: <span class='diff-rm'>\1</span>#"
		cat << EOT
</pre>

<h3>lsusb</h3>
<pre>$(lsusb)</pre>
EOT
		;;
esac

xhtml_footer
exit 0
