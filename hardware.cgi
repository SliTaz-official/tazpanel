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

# Call an optionnal module
lib()
{
	module=lib/$1
	shift
	[ -s $module ] && . $module "$@"
}

lsusb_table()
{
	cat << EOT
<table class="zebra outbox">
<thead><tr><td>Bus</td><td>Device</td><td>ID</td><td>Name</td></thead>
<tbody>
EOT
	lsusb | sed 's|^Bus \([0-9]*\)|<tr><td>\1</td>|;
			s|</td> Device \([0-9]*\):|</td><td>\1</td>|;
			s|</td> ID \([^:]*:[^ ]*\)|</td><td><a href="?lsusb=\1">\1</a></td>|;
			s| |<td>|2;
			s|.*$|\0</td></tr>|'
	echo "</tbody></table>"
}

lspci_table()
{
	cat << EOT
<table class="zebra outbox">
<thead><tr><td>Slot</td><td>Device</td><td>Name</td></thead>
<tbody>
EOT
	lspci | sed 's| |</td><td>|;
			s|: |</td><td>|;
			s|^\([^<]*\)|<a href="?lspci=\1">\1</a>|;
			s|^.*$|<tr><td>\0</td></tr>|'
	echo "</tbody></table>"
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
	*\ lsusb\ *)
		xhtml_header
		vidpid="$(GET lsusb)"
		cat << EOT
<div id="wrapper">
	<h2>$(eval_gettext 'Information for USB Device $vidpid')</h2>
	<p>$(gettext 'Detailed information about specified device.')</p>
EOT
		lsusb_table
		cat << EOT
</div>
<pre>$(lsusb -vd $vidpid | syntax_highlighter lsusb)</pre>
EOT
		;;
	*\ lspci\ *)
		xhtml_header
		slot="$(GET lspci)"
		cat << EOT
<div id="wrapper">
	<h2>$(eval_gettext 'Information for PCI Device $slot')</h2>
	<p>$(gettext 'Detailed information about specified device.')</p>
EOT
		lspci_table
		cat << EOT
</div>
<pre>$(lspci -vs $slot | syntax_highlighter lspci)</pre>
EOT
		;;
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


<h3 id="disk">$(gettext 'Filesystem usage statistics')</h3>

<pre>
$(fdisk -l | fgrep Disk)
</pre>
EOT


		#
		# Loop device management actions
		#
		device=$(GET loopdev)
		lib crypto $device
		case "$device" in
		/dev/loop*)
			set -- $(losetup | grep ^$device:)
			[ -n "$3" ] && losetup -d $device
			ro=""
			[ -n "$(GET readonly)" ] && ro="-r"
			file="$(GET backingfile)"
			[ -n "$file" ] && losetup -o $(GET offset) $ro $device $file
		esac
		#
		# Disk stats and management (mount, umount, check)
		#
		device=$(GET device)
		lib crypto $device
		case "$device" in
		*[\;\`\&\|\$]*) ;;
		mount\ *)
			ro=""
			[ -n "$(GET readonly)" ] && ro="-r"
			$device $ro $(GET mountpoint);;
		umount\ *|swapon\ *|swapoff\ *)
			$device ;;
		esac
		cat << EOT
<form method="get" action="$SCRIPT_NAME#mount">
<table id="mount" class="zebra outbox nowrap">
EOT
		df_thead
		echo '<tbody>'
		for fs in $(blkid | sed 's/:.*//')
		do
			set -- $(df -h | grep "^$fs ")
			size=$2
			used=$3
			av=$4
			grep "^$fs " /proc/mounts | grep -q "[, ]ro[, ]" &&
			av="<del>$av</del>"
			pct=$5
			mp=$6
			action="mount"
			[ -n "$mp" ] && action="umount"
			type=$(blkid $fs | sed '/TYPE=/!d;s/.*TYPE="\([^"]*\).*/\1/')
			[ "$type" == "swap" ] && action="swapon"
			if grep -q "^$fs " /proc/swaps; then
				action="swapoff"
				set -- $(grep "^$fs " /proc/swaps)
				size=$(blk2h $(($3*2)))
				used=$(blk2h $(($4*2)))
				av=$(blk2h $((2*($3-$4))))
				pct=$(((100*$4)/$3))%
				mp=swap
			fi
			[ -z "$size" ] &&
			size="$(blk2h $(cat /sys/block/${fs#/dev/}/size /sys/block/*/${fs#/dev/}/size))"
			img="harddisk.png"
			case "$(cat /sys/block/${fs#/dev/}/removable 2> /dev/null ||
				cat /sys/block/${fs:5:3}/removable 2> /dev/null)" in
			1) img="floppy.png" ;; 
			esac
			case "$(cat /sys/block/${fs#/dev/}/ro 2> /dev/null ||
				cat /sys/block/${fs:5:3}/ro 2> /dev/null)" in
			1) img="tazlito.png" ;; 
			esac
			[ -s ".$IMAGES/$img" ] || img="harddisk.png"
			cat << EOT
<tr>
	<td><input type="radio" name="device" value="$action $fs" />
	    <img src="$IMAGES/$img" />${fs#/dev/}</td>
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
	<td> </td>
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
$(lib crypto input)
<input type="submit" value="mount / umount" /> -
new mount point <input type=text" name="mountpoint" value="/media/usbdisk" /> -
<input type="checkbox" name="readonly"> read-only
</form>


<h3>$(gettext 'Filesystems table')</h3>
EOT

grep -v '^#' /etc/fstab | awk 'BEGIN{print "<table class=\"zebra outbox\">\
	<thead><tr><td>$(gettext 'Disk')</td><td>$(gettext 'Mount point')</td><td>\
	$(gettext 'Type')</td><td>$(gettext 'Options')</td><td>\
	$(gettext 'Freq')</td><td>$(gettext 'Pass')</td></thead><tbody>"}\
	{print "<tr><td>"$1"</td><td>"$2\
	"</td><td>"$3"</td><td>"$4"</td><td>"$5"</td><td>"$6"</td></tr>"}
	END{print "</tbody></table>"}'

		cat << EOT
<a class="button" href="index.cgi?file=/etc/fstab&action=edit">
	<img src="$IMAGES/edit.png" />$(gettext 'Manual Edit')</a>


<h3>$(gettext 'Loop devices')</h3>
EOT
		#
		# Loop device management gui
		#
		cat << EOT
<form method="get" action="$SCRIPT_NAME#loop">
<table id="loop" class="zebra outbox nowrap">
<thead>
<tr><td>Device</td><td>Backing file</td><td>Access</td><td>Offset</td></tr>
</thead>
<tbody>
EOT
for loop in $(ls /dev/loop[0-9]*); do
	case "$(cat /sys/block/${loop#/dev/}/ro 2> /dev/null)" in
	0) ro="read/write" ;;
	1) ro="read&nbsp;only" ;;
	*) ro="" ;;
	esac
	set -- $(losetup | grep ^$loop:) $ro
	cat << EOT
<tr>
	<td><input type="radio" name="loopdev" value="$loop" />
	    <img src="$IMAGES/harddisk.png" />${loop#/dev/}</td>
	<td>$3</td><td align="center">$4</td><td align="right">$2</td>
</tr>
EOT
done
		cat << EOT
</tbody>
</table>
$(lib crypto input)
<input type="submit" value="Setup" /> -
new backing file <input type="text" name="backingfile" /> -
offset in bytes <input type="text" name="offset" size="8" value="0" /> -
<input type="checkbox" name="readonly"> read-only
</form>
EOT

		cat << EOT
<h3>$(gettext 'System memory')</h3>
EOT

echo "<table class=\"zebra outbox\"><thead><tr><td>&nbsp;</td><td>total</td>\
<td>used</td><td>free</td><td>shared</td><td>buffers</td></tr></thead><tbody>"
freem=$(free -m)
echo "$freem" | grep Mem: | awk '{print "<tr><td>"$1"</td><td>"$2"</td><td>"$3\
	"</td><td>"$4"</td><td>"$5"</td><td>"$6"</td></tr>"}'
echo "$freem" | grep buffers: | awk '{print "<tr><td>"$1 $2"</td><td>&nbsp;</td>\
	<td>"$3"</td><td>"$4"</td><td>&nbsp;</td><td>&nbsp;</td></tr>"}'
echo "$freem" | grep Swap: | awk '{print "<tr><td>"$1"</td><td>"$2"</td><td>"$3\
	"</td><td>"$4"</td><td>&nbsp;</td><td>&nbsp;</td></tr></tbody></table>"}'

		cat << EOT
<h3>lspci</h3>
$(lspci_table)

<h3>lsusb</h3>
$(lsusb_table)
EOT
			;;
esac

xhtml_footer
exit 0
