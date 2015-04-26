#!/bin/sh
#
# Hardware part of TazPanel - Devices, drivers, printing
#
# Copyright (C) 2011-2015 SliTaz GNU/Linux - BSD License
#

# Common functions from libtazpanel
. lib/libtazpanel
get_config
header

TITLE=$(_ 'TazPanel - Hardware')

# Call an optional module
lib() {
	module=lib/$1
	shift
	[ -s $module ] && . $module "$@"
}

disk_info() {
	fdisk -l | fgrep Disk | while read a b c; do
		d=${b#/dev/}
		d="/sys/block/${d%:}/device"
		[ -d $d ] && echo "$a $b $c, $(cat $d/vendor) $(cat $d/model)"
	done 2> /dev/null | sed 's/  */ /g'
}

lsusb_table() {
	cat <<EOT
<table class="wide zebra">
	<thead>
		<tr>
			<td>$(_ 'Bus')</td>
			<td>$(_ 'Device')</td>
			<td>$(_ 'ID')</td>
			<td>$(_ 'Name')</td>
		</tr>
	</thead>
<tbody>
EOT
	lsusb | sed 's|^Bus \([0-9]*\)|<tr><td>\1</td>|;
			s|</td> Device \([0-9]*\):|</td><td>\1</td>|;
			s|</td> ID \([^:]*:[^ ]*\)|</td><td><a href="?lsusb=\1">\1</a></td>|;
			s| |<td>|2;
			s|.*$|\0</td></tr>|'
	echo "</tbody></table>"
}


lspci_table() {
	cat <<EOT
<table class="wide zebra">
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
		echo "<h2>TODO</h2>"
		;;


	*\ tazx\ *)
		xhtml_header
		cat <<EOT
<pre>$(tazx auto)</pre>
EOT
		;;


	*\ detect\ *)
		# Front end for Tazhw
		# TODO: Add button to detect webcam, etc. Like in tazhw box.
		xhtml_header
		cat <<EOT
<h2>$(_ 'Detect hardware')</h2>
<p>$(_ 'Detect PCI and USB hardware')</p>

<section>
	<pre>$(tazhw detect-pci | sed 's|^>|\&gt;|g')</pre>
	<pre>$(tazhw detect-usb | sed 's|^>|\&gt;|g')</pre>
</section>
EOT
		;;


	*\ modules\ *|*\ modinfo\ *)
		xhtml_header
		cat <<EOT
<h2>$(_ 'Kernel modules')</h2>
<p>$(_ 'Manage, search or get information about the Linux kernel modules')</p>

<form>
	<input type="hidden" name="modules"/>
	<input type="search" name="search" class="float-right" placeholder="$(_ 'Modules search')" results="5" autosave="modsearch" autocomplete="on"/>
</form>
EOT
		# Request may be modinfo output that we want in the page itself
		get_modinfo="$(GET modinfo)"
		if [ -n "$get_modinfo" ]; then
			cat <<EOT
<section>
	<header>$(_ 'Detailed information for module: %s' $get_modinfo)</header>

EOT
		modinfo $get_modinfo | awk 'BEGIN{print "<table class=\"wide zebra\">"}
		{
			printf("<tr><td><b>%s</b></td>", $1)
			$1=""; printf("<td>%s</td></tr>", $0)
		}
		END{print "</table></section>"}'
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
			_ 'Matching result(s) for: %s' $get_search
			echo '<pre>'
			modprobe -l | grep "$(GET search)" | while read line
			do
				name=$(basename $line)
				mod=${name%.ko.gz}
				echo "$(_ 'Module:') <a href='?modinfo=$mod'>$mod</a>"
			done
			echo '</pre>'
		fi
		cat <<EOT
<section>
	<table class="zebra">
		<thead>
			<tr>
				<td>$(_ 'Module')</td>
				<td>$(_ 'Description')</td>
				<td>$(_ 'Size')</td>
				<td>$(_ 'Used')</td>
				<td>$(_ 'by')</td>
			</tr>
		<thead>
		<tbody>
EOT
		# Get the list of modules and link to modinfo
		lsmod | tail -n+2 | awk '{
			gsub(",", " ", $4);
			printf("<tr><td><a href=\"?modinfo=%s\">%s</a></td><td>", $1, $1);
			system("modinfo -d " $1);
			printf("</td><td>%s</td><td>%s</td><td>%s</td></tr>", $2, $3, $4);
		}'
		cat <<EOT
		</thead>
	</table>
</section>
EOT
		;;


	*\ lsusb\ *)
		xhtml_header
		vidpid="$(GET lsusb)"
		cat <<EOT
<h2>$(_ 'Information for USB Device %s' $vidpid)</h2>

<p>$(_ 'Detailed information about specified device.')</p>

<section>$(lsusb_table)</section>
EOT
		[ "$vidpid" != 'lsusb' ] && cat <<EOT
<section>
	<pre style="white-space: pre-wrap">$(lsusb -vd $vidpid | syntax_highlighter lsusb)</pre>
</section>
EOT
		;;


	*\ lspci\ *)
		xhtml_header
		slot="$(GET lspci)"
		cat <<EOT
<h2>$(_ 'Information for PCI Device %s' $slot)</h2>

<p>$(_ 'Detailed information about specified device.')</p>

<section>$(lspci_table)</section>
EOT
		[ "$slot" != 'lspci' ] && cat <<EOT
<section>
	<pre style="white-space: pre-wrap">$(lspci -vs $slot | syntax_highlighter lspci)</pre>
</section>
EOT
		;;


	*)
		[ -n "$(GET brightness)" ] &&
			echo -n $(GET brightness) > /sys/devices/virtual/backlight/$(GET dev)/brightness

		#
		# Default to summary with mounted filesystem, loaded modules
		#
		xhtml_header
		cat <<EOT
<h2>$(_ 'Drivers &amp; Devices')</h2>
<p>$(_ 'Manage your computer hardware')</p>

<form><!--
	--><button name="modules" data-icon="modules">$(_ 'Kernel modules')</button><!--
	--><button name="detect"  data-icon="detect" data-root>$(_ 'Detect PCI/USB')</button><!--
	--><button name="tazx"    data-icon="tazx"   data-root>$(_ 'Auto-install Xorg video driver')</button><!--
--></form>

EOT


		# Battery state
		if [ -n "$(ls /proc/acpi/battery/*/info 2>/dev/null)" ]; then
			cat <<EOT
<section>
	<header>$(_ 'Battery')</header>
	<div>
		<table class="wide">
EOT
			for dev in /proc/acpi/battery/*; do
				grep ^present $dev/info | grep -q yes || continue
				 design=$(sed '/design capacity:/!d;       s/[^0-9]*\([0-9]*\).*/\1/' < $dev/info)
				 remain=$(sed '/remaining capacity/!d;     s/[^0-9]*\([0-9]*\).*/\1/' < $dev/state)
				   rate=$(sed '/present rate/!d;           s/[^0-9]*\([0-9]*\).*/\1/' < $dev/state)
				   full=$(sed '/last full capacity/!d;     s/[^0-9]*\([0-9]*\).*/\1/' < $dev/info)
				warning=$(sed '/design capacity warning/!d;s/[^0-9]*\([0-9]*\).*/\1/' < $dev/info)
				    low=$(sed '/design capacity low/!d;    s/[^0-9]*\([0-9]*\).*/\1/' < $dev/info)
				  state=$(sed '/charging state/!d;         s/\([^:]*:[ ]\+\)\([a-z]\+\)/\2/' < $dev/state)

				rempct=$(( $remain * 100 / $full ))
				cat <<EOT
			<tr>
				<td><span data-icon="battery">$(_ 'Battery')</span>
					$(grep "^battery type" $dev/info | sed 's/.*: *//')
					$(grep "^design capacity:" $dev/info | sed 's/.*: *//') </td>
				<td>$(_ 'health') $(( (100*$full)/$design))%</td>
				<td class="meter"><meter min="0" max="$full" value="$remain" low="$low"
					high="$warning" optimum="$full"></meter>
					<span>
EOT
				case "$state" in
				"discharging")
					remtime=$(( $remain * 60 / $rate ))
					remtimef=$(printf "%d:%02d" $(($remtime/60)) $(($remtime%60)))
					_ 'Discharging %d%% - %s' $rempct $remtimef ;;
				"charging")
					remtime=$(( ($full - $remain) * 60 / $rate ))
					remtimef=$(printf "%d:%02d" $(($remtime/60)) $(($remtime%60)))
					_ 'Charging %d%% - %s' $rempct $remtimef ;;
				"charged")
					_ 'Charged 100%%' ;;
				esac
				cat <<EOT

					</span>
				</td>
			</tr>
EOT
			done
			cat <<EOT
		</table>
	</div>
</section>
EOT
		fi


		# Thermal sensors
		if [ -n "$(ls /sys/devices/virtual/thermal/*/temp 2>/dev/null)" ]; then
			echo "<p><span data-icon=\"temperature\">$(_ 'Temperature:')</span>"
			for temp in /sys/devices/virtual/thermal/*/temp; do
				awk '{ print $1/1000 "℃" }' < $temp
			done
			echo '</p>'
		fi


		# Brightness
		if [ -n "$(ls /sys/devices/virtual/backlight/*/brightness 2>/dev/null)" ]; then
			echo '<form>'
			for dev in /sys/devices/virtual/backlight/*/brightness; do
				name=$(echo $dev | sed 's|.*/backlight/\([^/]*\).*|\1|')
				cat <<EOT
<input type="hidden" name="dev" value="$name"/>
<span data-icon="brightness">$(_ 'Brightness')</span> \
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
				echo '</select>'
			done
			echo '</form>'
		fi


		cat <<EOT
<section>
	<form action="#mount" class="wide">
		<header id="disk">$(_ 'Filesystem usage statistics')</header>
		<div>
			<pre>$(disk_info)</pre>
		</div>
EOT


		#
		# Loop device management actions
		#
		device=$(GET loopdev)
		lib crypto $device
		case "$device" in
		/dev/*loop*)
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
			mntdir="$(GET mountpoint)"
			[ -d "$mntdir" ] || mkdir -p "$mntdir"
			$device $ro "$mntdir";;
		umount\ *|swapon\ *|swapoff\ *)
			$device ;;
		esac
		cat <<EOT
		<table id="mount" class="zebra wide center">
EOT
		df_thead
		echo '<tbody>'
		for fs in $(blkid | sort | sed 's/:.*//'); do
			set -- $(df -h | grep "^$fs ")
			size=$2
			used=$3
			av=$4
			grep "^$fs " /proc/mounts | grep -q "[, ]ro[, ]" &&
			av="<del>$av</del>"
			pct=$5
			mp=$6

			# action
			action="mount"
			[ -n "$mp" ] && action="umount"
			type=$(blkid $fs | sed '/TYPE=/!d;s/.* TYPE="\([^"]*\).*/\1/')
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

			# size
			[ -z "$size" ] &&
			size="$(blk2h $(cat /sys/block/${fs#/dev/}/size /sys/block/*/${fs#/dev/}/size))"

			# image
			disktype="hdd"
			case "$(cat /sys/block/${fs#/dev/}/removable 2>/dev/null ||
				cat /sys/block/${fs:5:3}/removable 2>/dev/null)" in
			1) disktype="removable" ;;
			esac
			case "$(cat /sys/block/${fs#/dev/}/ro 2>/dev/null ||
				cat /sys/block/${fs:5:3}/ro 2>/dev/null)" in
			1) disktype="cd" ;;
			esac

			cat <<EOT
			<tr>
				<td><input type="radio" name="device" value="$action $fs" id="${fs#/dev/}"/><!--
					--><label for="${fs#/dev/}" data-icon="$disktype">&thinsp;${fs#/dev/}</label></td>
				<td>$(blkid $fs | sed '/LABEL=/!d;s/.*LABEL="\([^"]*\).*/\1/')</td>
				<td>$type</td>
				<td>$size</td>
				<td>$av</td>
EOT
		if [ -n "$pct" ]; then
			cat <<EOT
				<td class="meter"><meter min="0" max="100" value="${pct%%%}" low="70"
					high="90" optimum="10"></meter>
					<span>$used - $pct</span>
				</td>
EOT
		else
			cat <<EOT
				<td> </td>
EOT
		fi
		cat <<EOT
				<td>$mp</td>
				<td>$(blkid $fs | sed '/UUID=/!d;s/.*UUID="\([^"]*\).*/\1/')</td>
			</tr>
EOT
		done
		cat <<EOT
			</tbody>
		</table>
EOT
		[ "$REMOTE_USER" == "root" ] && cat <<EOT
		$(lib crypto input)

		<footer>
			<button type="submit">mount / umount</button> -
			$(_ 'new mount point:') <input type="text" name="mountpoint" value="/media/usbdisk"/> -
			<input type="checkbox" name="readonly" id="ro"><label for="ro">&thinsp;$(_ 'read-only')</label>
		</footer>
EOT
		cat <<EOT
	</form>
</section>
EOT


		#
		# /etc/fstab
		#
		cat <<EOT
<section>
	<header>
		$(_ 'Filesystems table')
EOT
		[ -w /etc/fstab ] && cat <<EOT
		<form action="index.cgi">
			<input type="hidden" name="file" value="/etc/fstab"/>
			<button name="action" value="edit" data-icon="edit">$(_ 'Edit')</button>
		</form>
EOT
		cat <<EOT
	</header>
	<table class="wide zebra center">
		<thead>
			<tr>
				<td>$(_ 'Disk')</td>
				<td>$(_ 'Mount point')</td>
				<td>$(_ 'Type')</td>
				<td>$(_ 'Options')</td>
				<td>$(_ 'Freq')</td>
				<td>$(_ 'Pass')</td>
			</tr>
		</thead>
		<tbody>
EOT

grep -v '^#' /etc/fstab | awk '{
	print "<tr><td>" $1 "</td><td>" $2 "</td><td>" $3 "</td><td>" $4
	print "</td><td>" $5 "</td><td>" $6 "</td></tr>"
}
	END{print "</tbody></table>"}'

		cat <<EOT
</section>
EOT


		#
		# Loop device management GUI
		#
		cat <<EOT
<section>
	<header>$(_ 'Loop devices')</header>

	<form action="#loop" class="wide">
	<div class="scroll">
		<table id="loop" class="wide zebra scroll">
			<thead>
				<tr>
					<td>$(_ 'Device')</td>
					<td>$(_ 'Backing file')</td>
					<td>$(_ 'Access')</td>
					<td>$(_ 'Offset')</td>
				</tr>
			</thead>
			<tbody>
EOT
for devloop in $(ls /dev/*loop[0-9]*); do
	loop="${devloop#/dev/}"
	case "$(cat /sys/block/$loop/ro 2>/dev/null)" in
	0) ro="$(_ "read/write")" ;;
	1) ro="$(_ "read only")" ;;
	*) ro="" ;;
	esac
	set -- $(losetup | grep ^$devloop:) ${ro// /&nbsp;}
	cat <<EOT
				<tr><td><input type="radio" name="loopdev" value="$devloop" id="$loop"/><!--
					--><label for="$loop" data-icon="loopback">$loop</label></td>
					<td>$3</td><td align="center">$4</td><td align="right">$2</td>
				</tr>
EOT
done
		cat <<EOT
			</tbody>
		</table>
	</div>

$(lib crypto input)

		<footer>
			<button type="submit" data-icon="ok">$(_ 'Setup')</button> -
			$(_ 'new backing file:') <input type="text" name="backingfile"/> -
			$(_ 'offset in bytes:') <input type="text" name="offset" value="0" size="8"/> -
			<input type="checkbox" name="readonly" id="ro"/><label for="ro">$(_ 'read only')</label>
		</footer>
	</form>
</section>
EOT


		#
		# System memory
		#
		mem_total=$(free -m | awk '$1 ~ "M" {print $2}')
		mem_used=$((100 * $(free -m | awk '$1 ~ "+" {print $3}') / mem_total))
		mem_buff=$((100 * $(free -m | awk '$1 ~ "M" {print $6}') / mem_total))
		mem_free=$((100 - mem_used - mem_buff))

		cat <<EOT
<section>
	<header>$(_ 'System memory')</header>

	<div class="sysmem"><!--
		--><span class="sysmem_used" style="width: ${mem_used}%" title="$(_ 'Used')"   ><span>${mem_used}%</span></span><!--
EOT
		[ $mem_buff != 0 ] && cat <<EOT
		--><span class="sysmem_buff" style="width: ${mem_buff}%" title="$(_ 'Buffers')"><span>${mem_buff}%</span></span><!--
EOT
		cat <<EOT
		--><span class="sysmem_free" style="width: ${mem_free}%" title="$(_ 'Free')"   ><span>${mem_free}%</span></span><!--
	--></div>

	<table class="wide zebra center">
		<thead>
			<tr>
				<td>&nbsp;</td>
				<td>total</td>
				<td>used</td>
				<td>free</td>
				<td>shared</td>
				<td>buffers</td>
			</tr>
		</thead>
		<tbody>
EOT

free -m | awk '
$1 ~ "M" {print "<tr><td>"$1"</td><td>"$2"</td><td>"$3"</td><td>"$4"</td><td>"$5"</td><td>"$6"</td></tr>"}
$1 ~ "+" {print "<tr><td>"$1 $2"</td><td></td><td>"$3"</td><td>"$4"</td><td></td><td></td></tr>"}
$1 ~ "S" {print "<tr><td>"$1"</td><td>"$2"</td><td>"$3"</td><td>"$4"</td><td></td><td></td></tr>"}'

		cat <<EOT
		</tbody>
	</table>
</section>
EOT


		#
		# lspci and lsusb summary tables
		#
		cat <<EOT
<section>
	<header>lspci</header>
	$(lspci_table)
</section>


<section>
	<header>lsusb</header>
	$(lsusb_table)
</section>
EOT
		;;
esac

xhtml_footer
exit 0
