#!/bin/sh
#
# CGI interface for SliTaz Live systems using Tazlito and TazUSB.
#
echo "Content-Type: text/html"
echo ""

# Common functions from libtazpanel
. lib/libtazpanel
get_config

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel-live'
export TEXTDOMAIN

TITLE="- Live"

#
# Commands executed in Xterm first
#

case "$QUERY_STRING" in
	write-iso=*)
		comp=${QUERY_STRING#write-iso=}
		xterm $XTERM_OPTS \
			-T "write-iso" \
			-e "tazlito writeiso $comp" & ;;
	gen-liveusb=*)
		dev=`httpd -d ${QUERY_STRING#gen-liveusb=}`
		xterm $XTERM_OPTS \
			-T "Tazusb gen-liveusb" \
			-e "tazusb gen-liveusb $dev; \
				gettext \"ENTER to quit\"; read i" & ;;
	*)
		continue ;;
esac

#
# Commands
#

case "$QUERY_STRING" in
	create)
		#
		# Create a flavor file and ISO in option with all settings
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
	<input type="submit" value="`gettext "write ISO"`" />
</form>

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
	<input type="submit" value="`gettext "generate"`" />
</form>

EOT
		;;
esac

xhtml_footer
exit 0
