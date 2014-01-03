#!/bin/sh
#
# help.cgi - Display TazPanel doc and README.
#
# Copyright (C) 2011-2014 SliTaz GNU/Linux - BSD License
#

# Common functions from libtazpanel
. lib/libtazpanel
get_config
header

# ENTER will search but user may search for a button, so put one.
search_form() {
	cat << EOT
<div class="search">
	<form method="get" action="$SCRIPT_NAME">
		<p>
			<input type="text" name="manual" size="20">
			<input type="submit" class="radius" value="$(gettext 'Manual')">
		</p>
	</form>
</div>
EOT
}

# Cat translated help content
TITLE=$(gettext 'TazPanel - Help &amp; Doc')

xhtml_header
search_form

if [ "$(GET manual)" ]; then
	echo '<pre>'
	man $(GET manual)
	echo '</pre>'
else
	if [ -d doc ]; then
		cat doc/tazpanel.html
	else
		cat /usr/share/doc/tazpanel/tazpanel.html
	fi

#	cat << EOT
#<h3>README</h3>
#<pre>$(cat $PANEL/README)</pre>
#EOT
	cat $PANEL/README.html

fi

xhtml_footer
exit 0
