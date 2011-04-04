#!/bin/sh
#
# CGI template interface for TazPanel (must go in $PANEL root to work).
#
echo "Content-Type: text/html"
echo ""

# Common functions from libtazpanel
. lib/libtazpanel
get_config

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel-template'
export TEXTDOMAIN

#
# Commands
#

case "$QUERY_STRING" in
	cmd)
		echo "" ;;
	*)
		#
		# Default xHTML content
		#
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Page title - Template"`</h2>
	<p>`gettext "Page information"`<p>
</div>

<h3>`gettext "h3 title"`</h3>

<pre>
Preformated output
</pre>
EOT
		;;
esac

xhtml_footer
exit 0
