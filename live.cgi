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
# Commands
#

case "$QUERY_STRING" in
	gen-distro)
		echo "" ;;
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

EOT
		;;
esac

xhtml_footer
exit 0
