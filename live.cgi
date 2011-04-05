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
		COMPRESSION=${QUERY_STRING#write-iso=}
		xterm $XTERM_OPTS \
			-title "write-iso" \
			-e "tazlito writeiso $COMPRESSION" & ;;
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

<h3>`gettext "Write an ISO"`</h3>
<p>
	`gettext "Writeiso will generate an ISO image of the current filesystem
	as is, including the /home directory. It is an easy way to remaster a
	SliTaz Live system, you just have to: boot, modify, writeiso."`
</p>
<form method="get" action="$SCRIPT_NAME">
	`gettext "Compression type:"`
	<select name="write-iso">
		<option value="gzip">gzip</option>
		<option value="lzma">lzma</option>
		<option value="none">none</option>
	</select>
	<input type="submit" value="`gettext "write ISO"`" />
</form
EOT
		;;
esac

xhtml_footer
exit 0
