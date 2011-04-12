#!/bin/sh
#
# CGI interface for SliTaz Live systems using Tazlito and TazUSB.
#
# Copyright (C) 2011 SliTaz GNU/Linux - GNU gpl v3
#


. /usr/bin/httpd_helper.sh

header

# Common functions from libtazpanel
. lib/libtazpanel
get_config

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel'
export TEXTDOMAIN

TITLE="- Live"

#
# Commands executed in Xterm first
#

case " $(GET) " in
	*\ write-iso\ *)
		comp=${QUERY_STRING#write-iso=}
		$TERMINAL $TERM_OPTS \
			-T "write-iso" \
			-e "tazlito writeiso $comp" & ;;
	*\ gen-liveusb\ *)
		dev=`httpd -d ${QUERY_STRING#gen-liveusb=}`
		$TERMINAL $TERM_OPTS \
			-T "Tazusb gen-liveusb" \
			-e "tazusb gen-liveusb $dev; \
				gettext \"ENTER to quit\"; read i" & ;;
	*\ loramoutput\ *)
		$TERMINAL $TERM_OPTS \
			-T "build loram iso" \
			-e "tazlito build-loram $(GET input) $(GET loramoutput) $(GET type)" & ;;
esac

#
# Commands
#

case "$QUERY_STRING" in
	create)
		#
		# Create a flavor file and ISO in options with all settings
		# Step by step interface and store files in cache.
		#
		gettext "TODO" ;;
	*)
		#
		# Default xHTML content
		#
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>`gettext "SliTaz Live Systems"`</h2>
	<p>`gettext "Create and manage Live CD or USB SliTaz systems"`<p>
</div>

<a name="liveusb"></a>
<h3>`gettext "Live USB"`</h3>
<p>
	`gettext "Generate SliTaz LiveUSB media and boot in RAM! Insert a
	LiveCD into the cdrom drive, select the correct device and press
	Generate."`
</p>
<form method="get" action="$SCRIPT_NAME">
	`gettext "USB Media to use:"`
	<select name="gen-liveusb">
EOT
		# List disk if plugged USB device
		if [ -d /proc/scsi/usb-storage ]; then
			for i in `blkid | cut -d ":" -f 1`; do
				echo "<option value='$i'>$i</option>"
			done
		else
			echo "<option value="">"`gettext "Not found"`"</option>"
		fi
		cat << EOT
	</select>
	<input type="submit" value="`gettext "Generate"`" />
</form>

<a name="livecd"></a>
<h3>`gettext "Write a Live CD"`</h3>
<p>
	`gettext "The command writeiso will generate an ISO image of the
	current filesystem as is, including all files in the /home directory.
	It is an easy way to remaster a SliTaz Live system, you just have
	to: boot, modify, writeiso."`
</p>
<form method="get" action="$SCRIPT_NAME">
	`gettext "Compression type:"`
	<select name="write-iso">
		<option value="gzip">gzip</option>
		<option value="lzma">lzma</option>
		<option value="none">none</option>
	</select>
	<input type="submit" value="`gettext "Write ISO"`" />
</form>

<h3>`gettext "Live CD tools"`</h3>
<a name="loram"></a>
<h4>`gettext "Convert ISO to loram"`</h4>
<p>
	`gettext "This command will convert an ISO image of a SliTaz Live CD
	to a new ISO image requiring less RAM to run."`
</p>
<form method="get" action="$SCRIPT_NAME#loram">
	<table>
	<tr>
	<td>`gettext "ISO to convert"`
	<input type="text" name="input" value="/root/" /></td>
	</tr>
	<tr>
	<td><input type="radio" name="type" value="ram" checked />`gettext "The filesystem is always in RAM"`.</td>
	</tr>
	<tr>
	<td><input type="radio" name="type" value="smallcdrom" />`gettext "The filesystem may be on a small CDROM"`.</td>
	</tr>
	<tr>
	<td><input type="radio" name="type" value="cdrom" />`gettext "The filesystem may be on a large CDROM"`.</td>
	</tr>
	<tr>
	<td>`gettext "ISO to create"`
	<input type="text" name="loramoutput" value="/root/loram.iso" /></td>
	</tr>
	</table>
	<input type="submit" value="`gettext "Convert ISO to loram"`" />
</form>

EOT
		;;
esac

xhtml_footer
exit 0
