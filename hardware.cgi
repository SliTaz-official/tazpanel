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

TITLE="- Hardware"

#
# Commands
#

case " $(GET) " in
	*\ print\ *)
		echo "TODO" ;;
	*\ detect\ *)
		# Front end for Tazhw
		# TODO: Add button to detect webcam, etc. Like in tazhw box.
		xhtml_header
				cat << EOT
<div id="wrapper">
	<h2>$(gettext "Detect hardware")</h2>
	<p>$(gettext "Detect PCI and USB hardware")</p>
</div>
EOT
		echo '<pre>'
		tazhw detect-pci
		echo '</pre>'
		echo '<pre>'
		tazhw detect-usb
		echo '</pre>' ;;
	*\ modules\ *|*\ modinfo\ *)
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Kernel modules"`</h2>
<div class="float-right">
	<form method="get" action="$SCRIPT_NAME">
		<input type="hidden" name="modules" />
		<input type="text" name="search" />
	</form>
</div>
	<p>$(gettext "Manage, search or get information about the Linux kernel modules")</p>
</div>
EOT
		# Request may be modinfo output that we want in the page itself
		if [ -n "$(GET modinfo)" ]; then
			echo '<strong>'
			gettext "Detailed information for module: "; echo "$(GET modinfo)"
			echo '</strong>'
			echo '<pre>'
			modinfo $(GET modinfo)
			echo '</pre>'
		fi
		if [ -n "$(GET modprobe)" ]; then
			echo '<pre>'
			modprobe -v $(GET modprobe)
			echo '</pre>' 
		fi
		if [ -n "$(GET rmmod)" ]; then
			echo "Removing"
			rmmod -w $(GET rmmod)
		fi
		if [ -n "$(GET search)" ]; then
			gettext "Matching result(s) for: "; echo "$(GET search)"
			echo '<pre>'
			modprobe -l | grep "$(GET search)" | while read line
			do
				name=$(basename $line)
				mod=${name%.ko.gz}
				echo "Module    : <a href='$SCRIPT_NAME?modinfo=$mod'>$mod</a> "
			done
			echo '</pre>'
		fi
		cat << EOT
	`table_start`
		<tr class="thead">
			<td>`gettext "Module"`</td>
			<td>`gettext "Size"`</td>
			<td>`gettext "Used"`</td>
			<td>`gettext "by"`</td>
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
			<td>`echo $BY | sed s/","/" "/g`</td>
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
	<h2>`gettext "Drivers &amp; Devices"`</h2>
	<p>`gettext "Manage your computer hardware`</p>
</div>
<div>
	<a class="button" href="$SCRIPT_NAME?modules">
		<img src="$IMAGES/tux.png" />Kernel modules</a>
	<a class="button" href="$SCRIPT_NAME?detect">
		<img src="$IMAGES/monitor.png" />Detect PCI/USB</a>
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
				# FIXME
				#remtime=$(( ($remain * 60) / $rate ))
				#rempct=$(( ($remain * 100) / $full ))
				cat << EOT
<tr>
	<td><img src="$IMAGES/battery.png" />
		Battery $(grep "^battery type" $dev/info | sed 's/.*: *//')
		$(grep "^design capacity:" $dev/info | sed 's/.*: *//') </td>
	<td>health  $(( (100*$full)/$design))%</td>
EOT
				if grep -qis discharging $dev/state; then
					cat <<EOT
	<td class="pct"><div class="pct"
		style="width: $rempct%;">charge&nbsp;$rempct%&nbsp;-&nbsp;$(printf "%d:%02d" $(($remtime/60)) $(($remtime%60)))</div></td>
EOT
				else
					cat <<EOT
	<td class="pct"><div class="pct"
		style="width: $rempct%;">recharging&nbsp;$rempct%</div></td>
EOT
				fi
			done
			echo "</table>"
		fi
		if [ -n "$(ls /sys/devices/virtual/thermal/*/temp 2> /dev/null)" ]; then
			echo "Temperature: "
			for temp in /sys/devices/virtual/thermal/*/temp; do
				awk '{ print $1/1000 }' < $temp
			done
		fi
		if [ -n "$(ls /sys/devices/virtual/backlight/*/brightness 2> /dev/null)" ]; then
			cat <<EOT
<form method="get" action="$SCRIPT_NAME">
EOT
			for dev in /sys/devices/virtual/backlight/*/brightness ; do
				name=$(echo $dev | sed 's|.*/backlight/\([^/]*\).*|\1|')
				cat <<EOT
<input type="hidden" name="dev" value="$name" />
$(gettext "Brightness") \
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

<h3>$(gettext "Filesystem usage statistics")</h3>
<pre>
EOT
		fdisk -l | fgrep Disk
		echo '</pre>'
		#
		# Disk stats and management (mount, umount, heck)
		#
		table_start
		df_thead
		df -h | grep ^/dev | while read fs size used av pct mp
		do
				cat << EOT
<tr>
	<td><img src="$IMAGES/harddisk.png" />${fs#/dev/}</td>
	<td>$size</td>
	<td>$av</td>
	<td class="pct"><div class="pct"
		style="width: $pct;">$used&nbsp;-&nbsp;$pct</div></td>
	<td>$mp</td>
</tr>
EOT
		done
		table_end
		echo "<h3>$(gettext "System memory")</h3>"
		echo '<pre>'
		free -m | sed \
			-e s"#total.*\([^']\)#<span class='top'>\0</span>#"g \
			-e s"#^[A-Z-].*:\([^']\)#<span class='sh-comment'>\0</span>#"g
		echo '</pre>'
		echo '<h3>lspci</h3>'
		echo '<pre>'
			lspci -k | sed \
			 -e s"#^[0-9].*\([^']\)#<span class='diff-at'>\0</span>#" \
			 -e s"#use: \(.*\)#use: <span class='diff-rm'>\1</span>#"
		echo '</pre>'
		echo '<h3>lsusb</h3>'
		echo '<pre>'
			lsusb
		echo '</pre>'
		;;
esac

xhtml_footer
exit 0
